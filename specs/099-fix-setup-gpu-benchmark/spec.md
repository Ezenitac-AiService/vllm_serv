# Feature Specification: setup.sh 폴리싱 및 GPU 모델 로드 실측 벤치마크 파이프라인 리팩토링 (099-fix-setup-gpu-benchmark)

**Feature Branch**: `099-fix-setup-gpu-benchmark`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "setup.sh 폴리싱과 리펙토링 - 발견된 문제점: nvtop으로 모니터링 중이었는데, gpu 부하, 메모리에 모델 로드가 전혀 이루어지지 않고 벤치마크가 진행됨 (전 전체 모델 TPS: 0.0, Supported: False 처리되는 문제 해결)"

## Clarifications

### Session 2026-08-05

- Q: setup.sh 구동 시 기존에 실행 중인 서버 프로세스(llama-server, FastAPI 등) 처리 방안 → A: setup.sh 시작 시(Step 0/1) 기존 가동 중인 서빙 프로세스 및 포트(8081 등) 점유 프로세스를 자동으로 감지하여 원자적으로 종료(stop_server.sh / ProcessManager SIGKILL)시킨 후 Clean 상태에서 환경 구축 및 GPU 벤치마크를 수행하도록 보장.
- Q: llama-server 스폰 후 VRAM 로딩 대기 및 Ready 확인 방식 → A: Option A (llama-server 스폰 직후 /health 엔드포인트를 0.2초 간격으로 최대 10초간 비동기 Polling하여 HTTP 200 OK 수신 즉시 웜업 인퍼런스를 전송하여 Race Condition 100% 방지).
- Q: 벤치마크 중 비정상 종료/Ctrl+C 시 자원 해제 방안 → A: Option A (signal 핸들러 및 atexit 훅에 ProcessManager.force_kill_zombie_llama_servers()를 등록하여 SIGINT/예외 종료 시에도 백그라운드 llama-server 및 점유 포트를 100% 자가 회수).
- Q: 임시 벤치마크 llama-server 네트워크 바인딩 범위 → A: Option A (ProcessManager가 llama-server 스폰 시 --host 127.0.0.1 루프백 인터페이스를 강제 지정하여 외부 네트워크 노출 및 무단 접근을 보안 차단).
- Q: setup.sh 벤치마크 완료 후 서빙 프로세스 재가동 정책 → A: Option A (setup.sh 최종 완료 단계에서 벤치마크 결과 선정된 최적 서빙 모델 및 설정값으로 ./start_server.sh를 자동 구동하고 서빙 헬스체크를 완수하여 서비스 연속성 보장).
- Q: OOM/타임아웃/가중치 부하 실패 모델 fallback 처리 정책 → A: Option A (터미널에 [BENCHMARK WARN] 상세 실패 원인을 명시하고 model_context_profiles.json에 is_supported=false, recommended_context_length=2048, scaling_tested=false로 명확히 마킹한 후 다음 모델 벤치마크 지속).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 카탈로그 내 모든 LLM 모델의 실체적 GPU 프로세스 스폰 및 VRAM 로드/인퍼런스 실측 보장 (Priority: P1) 🎯 MVP

시스템 관리자가 `./setup.sh --force-benchmark` 또는 `python scripts/benchmark_context_window.py --force-benchmark` 실행 시, 카탈로그 내 각 LLM 후보 모델(gemma4-e2b, gemma4-e4b, gemma4-12b, qwen3.5-2b, qwen3.5-4b, qwen3.5-9b 등)에 대해 실제 GPU 가속 백엔드(`llama-server`) 프로세스가 GPU 레이어 오프로딩(`-ngl 99`) 옵션과 함께 정상 스폰되고, GPU VRAM 할당 및 웜업 토큰 인퍼런스가 동작하여 nvtop / nvidia-smi 상에서 실제 GPU 부하 및 VRAM 점유가 관측되고 양수 TPS(> 0.0) 실측치가 측정 및 캐싱되도록 개선합니다.

**Why this priority**: 현재 `./setup.sh --force-benchmark` 구동 시 백그라운드 GPU 프로세스 스폰 실패 또는 웜업 요청 포트 미스/응답 오류로 인해 GPU 로드가 0%로 스킵되고 전체 후보 모델이 `TPS: 0.0`, `Supported: False`로 오마킹되는 치명적 오동작을 근본 해결합니다.

**Independent Test**: `./setup.sh --force-benchmark` 실행 중 nvtop 또는 nvidia-smi 모니터링 시 각 모델별로 GPU VRAM 점유량 상승 및 GPU Util 점유가 관측되고, 벤치마크 완료 후 `config/model_context_profiles.json` 내 지원 가능 모델들의 `is_supported`가 `true`로 수록되며 `tpot_tok_per_sec`가 0.0 초과의 실측치로 저장되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 카탈로그에 등록된 LLM 후보 모델 및 로컬 GGUF 파일이 준비된 상태에서, **When** `./setup.sh --force-benchmark`를 구동하면, **Then** 각 후보 모델 벤치마크 시 실제 `llama-server` 프로세스가 `-ngl 99` GPU 레이어 오프로딩 옵션으로 가동되고 웜업 추론이 성공하여 nvtop상에 VRAM 할당 및 GPU 사용량이 표시되어야 합니다.
2. **Given** GPU 프로세스가 스폰된 상태에서, **When** 웜업 추론 요청(`/v1/chat/completions`)이 전송되면, **Then** 8081(또는 설정된 포트)로 HTTP 요청이 정상 전달되고 토큰 생성속도(TPS > 0.0)와 VRAM 점유량이 실측 기록되어야 합니다.
3. **Given** 벤치마크가 완수되면, **Then** 하드웨어 VRAM 92% 이내에서 동작하는 모델들은 `is_supported=true`, `tpot_tok_per_sec > 0.0`, `scaling_tested=true`로 `config/model_context_profiles.json`에 정상 저장되어야 합니다.

---

### User Story 2 - setup.sh 내 이중 강제 벤치마크 호출 제거 및 중복 구동 방지 (Priority: P2)

관리자가 `./setup.sh --force-benchmark` 옵션으로 환경 구축을 실행할 때, Step 2.8(최적 서빙 모델 선정)에서 카탈로그 전체 모델 벤치마크 및 캐시 생성을 이미 완료한 경우 Step 4.5(컨텍스트 윈도우 스케일링)에서는 무필요한 6개 모델 재벤치마크를 중복 수행하지 않고 방금 생성된 캐시를 활용하여 고속 통과(Smart Skip)되도록 `setup.sh` 제어 로직을 정리합니다.

**Why this priority**: 현행 `setup.sh`는 `--force-benchmark` 지정 시 Step 2.8과 Step 4.5 양쪽 모두에서 카탈로그 전체 모델에 대한 실측 벤치마크를 중복(2회 연속) 호출하여 불필요하게 2배의 대기 시간을 소모합니다.

**Independent Test**: `./setup.sh --force-benchmark` 구동 시 Step 2.8에서 전체 실측 벤치마크가 수행된 후 Step 4.5에서는 "캐시 프로필 완비"로 감지하여 5초 이내에 추가 재벤치마킹 없이 완료되는지 로그를 검증합니다.

**Acceptance Scenarios**:

1. **Given** `./setup.sh --force-benchmark` 구동 시 Step 2.8에서 카탈로그 전체 모델 벤치마크가 성공적으로 완납된 경우, **When** Step 4.5에 도달하면, **Then** 전체 재벤치마킹을 실행하지 않고 기존 캐시 프로필 정합성 검증 후 5초 이내 스킵 처리되어야 합니다.

---

### User Story 3 - 프로세스 스폰 에러 진단 로그 강화 및 포트/프로세스 자원 격리 보장 (Priority: P3)

GPU 벤치마크 실행 중 프로세스 스폰 실패, 포트 충돌, GGUF 파일 경로 이탈 또는 CUDA 초기화 실패 발생 시, 원인을 은폐하지 않고 구체적인 실패 사유(포트 점유, GGUF 경로 불일치, OOM 등)를 터미널 로그에 명확히 출력하고 안전하게 잔여 프로세스를 SIGKILL 정돈합니다.

**Why this priority**: 벤치마크 오동작 시 원인을 손쉽게 파악하고 포트 충돌이나 좀비 프로세스로 인한 연속 실패를 방지하기 위함입니다.

**Independent Test**: 의도적으로 존재하지 않는 모델 경로를 설정하거나 포트를 점유시킨 상태에서 벤치마크 구동 시 명확한 진단 로그가 출력되고 다음 모델 벤치마크로 안전하게 이행하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 특정 모델의 GGUF 파일 경로가 잘못되거나 포트 바인딩에 실패한 상황에서, **When** 벤치마크가 구동되면, **Then** 예외 원인이 상세 로그로 표시되고 잔여 프로세스가 깨끗이 종료된 후 파이프라인이 중단 없이 지속되어야 합니다.

---

### Edge Cases

- **기존 서버 프로세스 포트 점유**: 8081 포트가 이전 서빙 프로세스에 의해 점유되어 있는 경우, `ProcessManager`가 이전 프로세스를 확실히 SIGTERM/SIGKILL 정돈하거나 포트 해제를 대기한 후 벤치마크를 가동합니다.
- **VRAM 물리 용량 초과 모델**: 12B 이상의 대형 모델 로딩 시 물리 VRAM(예: 11GB)을 100% 초과하여 `llama-server`가 즉시 OOM 에러로 종료되는 경우, `Supported: False`로 안전 마킹하고 다음 모델로 이행합니다.
- **GGUF 로컬 가중치 파일 미비**: 카탈로그에는 수록되어 있으나 로컬 `models/` 경로에 `.gguf` 가중치 파일이 없는 경우, 실측 GPU 스폰을 시도하지 않고 VRAM 추정 프로필을 할당합니다.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/benchmark_context_window.py` 및 `src/core/process_manager.py` 수정 후 `./setup.sh --force-benchmark` 구동 시 실제 GPU 프로세스 가동, VRAM 점유 및 양수 TPS(> 0.0) 실측 성공 검증
- **DoD-002**: `scripts/setup.sh` 내 Step 2.8 및 Step 4.5 중복 강제 벤치마크 구동 제거 및 캐시 재활용 고속 스킵(Smart Skip) 구현 완료
- **DoD-003**: 단위/통합 테스트 수트 및 전체 회귀 테스트 수트(`uv run pytest`) 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `ProcessManager` 및 `benchmark_context_window.py`는 GPU 벤치마크 시 `llama-server` 백엔드 프로세스를 가동할 때 `-ngl 99` (GPU 레이어 오프로딩), `--host 127.0.0.1` (루프백 보안 바인딩) 및 올바른 로컬 GGUF 파일 경로를 명시적으로 인자로 전달하여 VRAM에 모델을 실체적으로 로드해야 합니다.
- **FR-002**: `ProcessManager`는 `llama-server` 스폰 직후 `/health` 엔드포인트를 0.2초 간격 최대 10초간 비동기 Polling하여 HTTP 200 OK 상태를 확인한 즉시 설정된 동적 포트로 HTTP POST 웜업 요청을 전송하고 실측 TPS를 계산해야 합니다.
- **FR-003**: 벤치마크 스텝 간 기존 `llama-server` 프로세스 종료 시 포트가 완전히 해제될 때까지 대기하고, Python `signal` 핸들러(SIGINT/SIGTERM) 및 `atexit` 훅에 자원 회수 로직을 등록하여 사용자 중단 시에도 좀비 프로세스와 점유 포트를 100% 소멸시켜야 합니다.
- **FR-004**: `./setup.sh --force-benchmark` 실행 시 Step 2.8에서 전체 카탈로그 벤치마크 및 `config/model_context_profiles.json` 캐시 생성을 완납한 경우, Step 4.5에서는 캐시를 재활용하여 5초 이내 스킵 처리되어야 합니다.
- **FR-005**: 벤치마크 과정에서 실측 성공한 모델은 `config/model_context_profiles.json`에 `is_supported=true`, `tpot_tok_per_sec > 0.0`, `peak_vram_mb > 0`으로 수록되고, 실제 OOM/타임아웃 또는 스폰 실패 모델에 한해서만 터미널에 `[BENCHMARK WARN]` 진단 로그를 출력하고 `is_supported=false`, `recommended_context_length=2048`, `scaling_tested=false`로 기록해야 합니다.
- **FR-006**: `setup.sh`는 실행 초기(Step 0 또는 Step 1)에 기존 가동 중인 `llama-server` 및 FastAPI 서빙 프로세스를 자동으로 감지하여 원자적으로 안전 종료(Pre-execution cleanup)시켜 포트 충돌 없는 대기 상태를 보장해야 합니다.
- **FR-007**: `setup.sh`는 벤치마크 및 설정을 완료한 후 최종 완료 단계(Step 5)에서 갱신된 최적 모델과 컨텍스트 윈도우 크기를 반영하여 `./start_server.sh`를 자동 호출하고 서빙 헬스체크를 완수하여 서비스 연속성을 보장해야 합니다.

### Key Entities

- **ModelContextProfiles**: 각 LLM 후보 모델별 `max_context_length`, `recommended_context_length`, `peak_vram_mb`, `tpot_tok_per_sec`, `is_supported`, `scaling_tested` 실측 데이터를 담는 JSON 스키마 객체.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./setup.sh --force-benchmark` 구동 시 로컬 가중치가 존재하는 지원 가능 LLM 모델(예: `qwen3.5-4b`, `gemma4-e2b` 등)의 실측 `tpot_tok_per_sec`가 0.0 초과의 양수로 측정되어야 합니다.
- **SC-002**: 벤치마크 구동 중 nvtop / nvidia-smi 상에서 모델 로딩 시 VRAM 사용량 상승 및 인퍼런스 수행 시 GPU Util 점유가 100% 관측되어야 합니다.
- **SC-003**: `./setup.sh --force-benchmark` 전체 구동 시간이 Step 4.5 중복 벤치마크 제거를 통해 기존 대비 40% 이상 단축되어야 합니다.

## Assumptions

- **NVIDIA GPU CUDA 가속 환경**: 벤치마크가 가동되는 장비에는 NVIDIA GPU 및 CUDA 가속 지원 `llama-cpp-python` / `llama-server` 바이너리가 빌드되어 있습니다.
- **로컬 GGUF 모델 가중치**: `models/` 디렉토리에 벤치마크 대상 GGUF 파일이 존재하거나 Step 2.6 자동 프로비저닝을 통해 다운로드됩니다.
