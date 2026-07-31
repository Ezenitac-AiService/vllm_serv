# Feature Specification: GPU VRAM 오프로드 완료 타이밍 보정 및 프로세스 바인딩 격리 (GPU VRAM Offload & Process Lifecycle Timing Fix)

**Feature Branch**: `011-fix-vram-offload-timing`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "vram 해제 타이밍이 이상함, 결국 어떤 모델도 gpu의 vram에 탑재되지 못했음. 모델 로드, 언로드, vram 반환 주기를 언제하지? 평상시에는 서버가 기본 모델을 계속 온로드로 서비스 해야 해"

## Clarifications

### Session 2026-07-29

- Q: 평상시 서빙 운영 시 모델 로드/언로드 및 VRAM 반환 주기는 어떻게 동작해야 하는가? → A: 평상시 서빙 서버는 기본 상주 모델(Default Resident Model: `qwen3.5-4b`)을 항상 GPU VRAM에 100% On-Load 상태로 지속 서빙합니다. 요청 단위 로드/언로드는 발생하지 않으며, 언로드/VRAM 반납은 (1) 모델 스위칭 API 호출 시, 또는 (2) 벤치마크 수행 시 모델 순차 교체 단계에서만 수행됩니다. 벤치마크 종료 후에는 기본 상주 모델로 자동 원상 복원(Restore)됩니다.
- Q: 심층 심의 보정(Remediation) - VRAM 측정 속도 및 헬스체크 신뢰성 개선 → A: PyNVML C-API 바인딩 사용으로 AsyncIO 이벤트 루프 블로킹 방지(< 1ms), `llama-server` 네이티브 `/health` JSON 엔드포인트 검증 병행, 커널 소켓 `TIME_WAIT` 제어 적용.
- Q: Ollama / LM Studio / LiteLLM 우수 아키텍처 수용 반영 → A: Graceful Stream Drain (스위칭 시 진행 중인 요청 완료 대기), KV Cache 수학적 VRAM 사전 추정기($n_{ctx}$ KV 캐시 포함 계산), K8s/LiteLLM 호환 `/health/liveness` & `/health/readiness` 엔드포인트 도입.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - GPU VRAM 100% 오프로드 완료 기반 READY 상태 전환 (Priority: P1) 🎯 MVP

시스템 엔지니어 및 테스터는 서빙 프로세스 개설 시 단순 HTTP 포트 응답(0.06초 조기 200 OK)에 의존하지 않고, `llama-server`가 모델 트랜스포머 전체 레이어 및 CLIP 가중치를 GPU VRAM에 100% 탑재(Offload) 완료한 시점 이후에만 프로세스가 `READY` 상태로 전환되도록 보장받을 수 있어야 합니다.

**Why this priority**: 모델 가중치가 GPU VRAM에 로드되기 전 추론이 시작되어 CPU fallback 기반의 저성능(TTFT > 7~8초) 추론이 실행되는 현상을 완벽히 차단하고 100% GPU 가속 추론을 보장하기 위함입니다.

**Independent Test**: 프로세스 개설 로그 모니터링 시 VRAM 레이어 탑재 확인 및 `/health` JSON 상태 검증 전에는 HTTP READY 상태로 동기화되지 않으며, VRAM 탑재 완료 직후 READY로 전환되어 빠른 TTFT(< 500ms) 및 TPOT(> 30 tok/s) 추론이 수행되는지 검증 가능합니다.

**Acceptance Scenarios**:

1. **Given** 신규 모델 개설 요청 시, **When** `llama-server` 프로세스가 개설되면, **Then** stdout 로그에서 `offloaded N/N layers to GPU` 및 네이티브 `/health` JSON API가 실시간으로 검증된 이후에만 프로세스 상태가 `READY`로 전환됩니다.
2. **Given** 모델 레이어가 VRAM에 탑재 중인 상항에서, **When** HTTP `/v1/models` 또는 `/health/readiness` 헬스체크 폴링이 수행되면, **Then** VRAM 오프로드가 완료되기 전까지는 READY 상태 확정을 유예하고 대기합니다.

---

### User Story 2 - 기존 프로세스/포트 바인딩 완벽 해제 및 Graceful Drain 동기화 (Priority: P2)

사용자는 모델 스위칭 또는 벤치마크 재개설 시 진행 중인 추론 스트림이 안전 종료(Graceful Drain)되고, 이전 서빙 프로세스 및 바인딩 포트(8081)가 완전히 종료되며 GPU VRAM 점유가 해제된 것을 확정한 후 신규 서빙 프로세스를 개설할 수 있어야 합니다.

**Why this priority**: 이전 서빙 프로세스가 소켓을 포기하지 않은 상태에서 신규 프로세스가 개설되어 이전 서버에 잘못 응답하거나, VRAM 해제 타이밍 불일치로 신규 모델이 GPU 대신 CPU RAM으로 롤백되는 현상을 방지하기 위함입니다.

**Independent Test**: 이전 모델 종료 시 활성 커넥션 0 완료 대기, 포트 소켓 미사용 상태(`SO_REUSEADDR` 정리) 및 PyNVML/nvidia-smi VRAM 0MB 반납이 완벽히 검증된 후 신규 모델 로딩 단계를 시작하는지 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 기존 서빙 프로세스가 가동 중일 때, **When** 신규 모델 스위칭(`spawn_process`)이 호출되면, **Then** 진행 중인 추론 완료 대기(Graceful Drain), 이전 프로세스 PID 종료, 포트 해제 확인, PyNVML VRAM 반납이 완벽히 순차 수행된 후 신규 프로세스가 개설됩니다.
2. **Given** 이전 프로세스 종료 시 잔여 핑거프린트 포트 연결이 감지되는 경우, **When** 소켓 연결 확인 로직이 동작하면, **Then** 포트가 완전히 해제될 때까지 최대 대기 시간 동안 동기화합니다.

---

### User Story 3 - 벤치마크 루프 실측 타이밍 및 평시 서비스 원상 복원 (Priority: P3)

사용자는 `scripts/benchmark_quality.py` 실행 시 각 모델 단계별로 VRAM 로드 동기화가 정상 수행되어 6개 라인업 전반의 정확한 GPU 실측 결과 데이터를 수집하고, 벤치마크 종료 후 평상시 기본 서비스 모델로 원상 복원되는지 보장받을 수 있어야 합니다.

**Why this priority**: 벤치마크 도중 조기 HTTP READY 판정이나 VRAM 해제 타이밍 이상으로 타임아웃 예외가 발생하는 문제를 해결하고, 벤치마크 종료 후 운영 서빙 상태를 원활히 유지하기 위함입니다.

**Independent Test**: `--auto-download --real` 벤치마크 실행 시 타임아웃 오류 없이 모든 지원 모델이 GPU VRAM에 로드되어 추론을 완수하며, 벤치마크 완료 후 기본 모델(`qwen3.5-4b`)로 원상 복구되는지 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** `benchmark_quality.py --real` 실행 시, **When** 모델 개설 및 실측 추론이 수행되면, **Then** 타임아웃 없이 GPU 기반 추론(TTFT < 1초, TPOT > 30 tok/s)이 정상 기록되고 벤치마크 보고서가 생성됩니다.
2. **Given** 벤치마크 평가 루프가 완료된 직후, **When** 최종 보고서 생성이 끝제면, **Then** 기본 서빙 모델(`qwen3.5-4b`)이 자동으로 VRAM에 재로드되어 평시 운영 상태로 복원됩니다.

---

### Edge Cases

- **초고속 HTTP 응답 착오**: 이전 좀비 프로세스나 타 서비스가 8081 포트를 점유 중일 경우 신규 프로세스 개설 실패 예외 처리.
- **VRAM 완납 확인 지연**: GPU 메모리 가비지 컬렉션 지연 시 최대 5초간 재확인 후 안전 개설.
- **PyNVML 미설치 환경**: PyNVML 바인딩 임포트 실패 시 nvidia-smi CLI 폴백으로 안전 전환.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `ProcessManager` 및 `LlamaManager` 내 PyNVML 기반 non-blocking VRAM 검증, `/health` JSON 엔드포인트 수집, VRAM 100% 오프로드 동기화 완료.
- **DoD-002**: 프로세스 종료 시 Graceful Drain, 포트 완납(SO_REUSEADDR 제어) 및 VRAM 완전 해제 확인 후 신규 프로세스 생성 타이밍 보정 로직 단위/통합 테스트 작성 및 통과.
- **DoD-003**: GGUF + KV Cache 수학적 VRAM 사전 추정기($VRAM_{KV}$) 구현 및 OOM 사전 차단 검증.
- **DoD-004**: `scripts/benchmark_quality.py --real` 실행 시 조기 타임아웃 없이 실제 GPU VRAM 오프로드 및 실측 추론 완수 후 기본 서비스 모델 원상 복원 검증.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `llama-server` 서빙 프로세스 개설 시 HTTP 200 응답만으로 즉시 `READY` 판정을 내리지 않고, VRAM 레이어 오프로드 완료 이벤트(`vram_offloaded_100pct == True`)가 확인된 후 `READY`로 전환해야 합니다.
- **FR-002**: 시스템은 `spawn_process` 실행 시 이전 프로세스의 SIGTERM/SIGKILL 완료, 포트 8081 소켓 완전 해제, GPU VRAM 메모리 반납을 완벽히 동기화 수순으로 수행한 후 신규 자식을 생성해야 합니다.
- **FR-003**: 시스템은 `llama-server` 실행 시 GPU VRAM 탑재가 완료되기 전 불완전 상태에서의 추론 요청을 차단하고 헬스체크 대기 시간을 동적으로 조정해야 합니다.
- **FR-004**: 시스템은 벤치마크 스크립트 실행 시 모델별 로드 대기 시점에서 VRAM 탑재 완료 상태를 명시적으로 기다려 추론 타임아웃을 방지해야 합니다.
- **FR-005**: 시스템은 잔여 좀비 프로세스가 기존 포트에 남아있는 경우 이를 탐지하여 안전 종료 및 차단 예외를 발생시켜야 합니다.
- **FR-006**: 시스템은 평상시 서빙 구동 시 기본 서비스 모델(`qwen3.5-4b`)을 GPU VRAM에 항상 On-Load 상태로 상주 서빙해야 하며, 요청 단위 언로드/VRAM 반납을 수행하지 않아야 합니다.
- **FR-007**: 시스템은 벤치마크 종료 시 평상시 기본 서비스 모델을 자동으로 GPU VRAM에 재로드하여 상주 서빙 상태로 원상 복구해야 합니다.
- **FR-008**: 시스템은 AsyncIO 이벤트 루프 블로킹 방지를 위해 PyNVML (`pynvml`) C-API 바인딩을 통해 VRAM 점유량을 < 1ms 속도로 측정해야 하며, 미설치 시 nvidia-smi로 안전 폴백해야 합니다.
- **FR-009**: 시스템은 `llama-server` 헬스체크 시 stdout 로그 파싱과 함께 네이티브 `/health` JSON 엔드포인트를 병행 검증해야 합니다.
- **FR-010**: 시스템은 포트 소켓 해제 확인 시 TCP 커널 `TIME_WAIT` 상태 및 소켓 재바인딩 여부를 명시적으로 제어해야 합니다.
- **FR-011**: 시스템은 모델 스위칭(`stop_process`) 시 진행 중인 HTTP SSE 추론 스트림 커넥션이 안전하게 완료될 때까지 대기하는 Graceful Stream Drain 메커니즘(`active_requests == 0`, 최대 5초 대기)을 수행해야 합니다.
- **FR-012**: 시스템은 `llama-server` 프로세스 개설 전, GGUF 가중치 용량과 $n_{ctx}$ 컨텍스트 크기에 따른 KV 캐시 점유량($2 \cdot L \cdot H \cdot D \cdot n_{ctx}$)을 합산하는 KV Cache Pre-flight VRAM Estimator를 구동하여 GPU VRAM 초과 시 개설을 사전 단에서 차단해야 합니다.
- **FR-013**: 시스템은 K8s 및 LiteLLM 엔터프라이즈 프록시와의 표준 호환성을 위해 `GET /health/liveness` (프로세스 생존 200 OK) 및 `GET /health/readiness` (100% VRAM 오프로드 및 READY 200 OK) 엔드포인트를 제공해야 합니다.

### Key Entities

- **ProcessLifecycleState**: status (UNLOADED, DOWNLOADING, LOADING, VRAM_OFFLOADED, READY, ERROR), pid, port, vram_offloaded_100pct, active_requests
- **VramLoadTimingGuard**: baseline_vram, target_vram, offload_verified_at, socket_cleared, nvml_handle, kv_cache_vram_mb

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 모델 개설 시 조기 READY 판정(load_time < 0.1s 오류)이 0건으로 방지되어 100% VRAM 오프로드 동기화가 보장되어야 합니다.
- **SC-002**: GPU 가속 추론 시 TTFT가 1.0초 이내(기존 8초 CPU 저하 해소) 및 TPOT 30 tok/s 이상을 달성해야 합니다.
- **SC-003**: 벤치마크 6개 라인업 연속 실행 시 VRAM 타이밍 오류로 인한 타임아웃 실패율 0%를 유지하며, 완료 후 기본 서비스 모델 복원률 100%를 달성해야 합니다.
- **SC-004**: PyNVML 적용을 통해 VRAM 측정 시 AsyncIO 이벤트 루프 오버헤드를 1ms 이내로 단축해야 합니다.
- **SC-005**: KV Cache VRAM 추정기 및 Graceful Stream Drain을 통해 핫스왑 중 요청 중단율 0% 및 OOM 발생률 0%를 달성해야 합니다.

## Assumptions

- 환경 내 NVIDIA GPU 및 CUDA 백엔드가 활성화되어 있으며 `llama-server` 실행 옵션(`-ngl 999`)이 정상 인수로 전달된다고 가정합니다.
- 포트 8081은 `vllm_serv` 전용 서빙 포트로 사용되며, 기본 서빙 모델은 `qwen3.5-4b`입니다.
