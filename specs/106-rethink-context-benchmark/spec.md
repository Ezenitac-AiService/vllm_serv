# Feature Specification: 컨텍스트 윈도우 벤치마킹 로직 전면 재검토 및 가용성 보장 (Rethink Context Benchmark Logic)

**Feature Branch**: `106-rethink-context-benchmark`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "컨텍스트 윈도우 벤치마킹 결과가 많이 이상해, 로직을 전면 재검토하는 스펙 작성 모델 컨텍스트 프로필 json의 diff를 확인해봐"

## Clarifications

### Session 2026-08-07

- Q: `llama_cpp.server` (Python fallback) 및 `llama-server` (C++ binary) 간 헬스 체크 엔드포인트 호환성 부재 해결 방안 → A: Option A (`/health` 응답이 404일 경우 `/v1/models` 엔드포인트를 폴백 조회하여 200 OK 확인 시 Readiness 성공 판정)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 실시간 GPU VRAM 및 백그라운드 서빙 서버 점유 상태 감지 (Priority: P1)

시스템 관리자 및 사용자는 백그라운드 인퍼런스 서버(`vllm_serv`)가 구동 중이거나 타 프로세스가 GPU VRAM을 점유하고 있을 때, 벤치마크 스크립트 실행 시 현재 실제 사용 가능한 가용 VRAM(Free VRAM)을 실시간으로 감지하여 OOM 크래시 없이 안전하게 벤치마킹을 수행하거나 적절한 경고/격리 안내를 받아야 한다.

**Why this priority**: 현재 벤치마크 로직은 GPU 전체 하드웨어 용량(`total_vram_mb - 500`)만을 기준으로 삼아 백그라운드 서버 구동 중 벤치마킹 시 GPU VRAM 고갈로 인한 CUDA OOM 및 커널 OOM Killer(Exit Code 137) 폭주를 야기하므로 최우선으로 해결해야 한다.

**Independent Test**: 백그라운드 인퍼런스 서버(포트 8089/8090/8091)가 작동 중인 상태에서 `uv run python scripts/benchmark_context_window.py --force-benchmark`를 실행했을 때, 커널 OOM 또는 서버 크래시 없이 실시간 가용 VRAM을 판단하여 사전 거부/안내 또는 가용 자원 범위 내 측정으로 안전하게 종료되는지 검증한다.

**Acceptance Scenarios**:

1. **Given** 백그라운드 서빙 서버가 VRAM 4.4GB를 점유 중인 상태에서, **When** `--force-benchmark` 명령을 실행하면, **Then** 하드웨어 전체 VRAM이 아닌 실시간 측정된 가용 VRAM(Free VRAM)을 기준으로 평가 가능 여부를 판단하고 경고 메시지를 출력한다.
2. **Given** 가용 VRAM이 모델 베이스 VRAM 요구량보다 부족한 환경에서, **When** 이진 탐색 로딩을 시도하기 전, **Then** 사전 검증 단계(Pre-flight Check)에서 OOM 위험을 감지하여 불필요한 서브프로세스 강제 로딩 및 OOM 폭주를 차단한다.

---

### User Story 2 - 벤치마크 실패 시 기존 프로파일 안전 보존 및 원자적 갱신 (Priority: P2)

사용자는 벤치마킹 도중 일시적 프로세스 오류, 타임아웃, VRAM 부족 충돌 등의 실패가 발생하더라도, 기존에 성공적으로 측정한 고품질 프로파일 데이터(`model_context_profiles.json`)가 파괴되거나 일률적으로 `is_supported: false`, `n_ctx: 2048` 더미 데이터로 덮어씌워지지 않기를 바란다.

**Why this priority**: 이전 측정 결과(예: Qwen 9B 12K, Gemma 2B 15K 정상 프로파일)가 일시적 벤치마크 오류 한 번으로 인해 전체 파괴(Destructive Overwrite)되는 현상을 방지해야 시스템 신뢰성을 유지할 수 있다.

**Independent Test**: 기존 정상 프로파일 데이터가 존재하는 상태에서 특정 모델의 벤치마크가 실패하도록 유도했을 때, 기존 정상 프로파일 데이터가 유실되지 않고 이전 안전 값이 유지되거나 실패 사유만 독립 기록되는지 검증한다.

**Acceptance Scenarios**:

1. **Given** 기존 `model_context_profiles.json`에 정상 측정된 `max_context_length` 결과가 존재할 때, **When** 새로운 벤치마크 실행 중 예외 또는 VRAM 고갈이 일어나면, **Then**기존 검증된 프로파일 항목을 파괴하지 않고 보존한다.
2. **Given** 벤치마크 평가가 성공적으로 완료되었을 때만, **Then** 해당 모델의 측정 데이터만 원자적으로(Atomic Update) 신규 갱신한다.

---

### User Story 3 - 서브프로세스 정리 시 타 서빙 프로세스 무차별 종료 방지 및 헬스체크 호환성 (Priority: P3)

시스템은 벤치마크 수행 중 또는 종료 시(atexit/Signal handler) 잔여 프로세스를 정리할 때, 자신이 생성한 벤치마크 전용 서브프로세스(포트 8081)만 핀포인트로 종료해야 하며, 상주 서빙 중인 메인 서버 프로세스(포트 8089, 8090, 8091)를 사살하지 않아야 한다. 또한 `llama_cpp.server` (Python fallback) 구동 시에도 `/health` 엔드포인트 부재로 인한 폴링 타임아웃이 발생하지 않아야 한다.

**Why this priority**: 현재 `pkill -9 -f llama-server` 방식의 와일드카드 cleanup은 벤치마크 실행 즉시 메인 서비스 인프라를 다운시키고, `/health` 전용 폴링은 `llama_cpp.server` 구동 시 100% 헬스 체크 실패를 초과 유발한다.

**Independent Test**: 메인 서빙 서버가 구동 중인 상태에서 벤치마크 스크립트를 실행 및 종료시켰을 때, 메인 서버 프로세스(PID)가 살아있는지 및 `llama_cpp.server` 환경에서도 정상 헬스체크 Readiness 통과가 일어나는지 검증한다.

**Acceptance Scenarios**:

1. **Given** 메인 인퍼런스 서버가 8089 포트에서 구동 중일 때, **When** 벤치마크 프로세스가 종료되거나 cleanup hook이 실행되면, **Then** 8081 포트의 벤치마크 서브프로세스 PID만 정밀 종료하고 8089/8090/8091 포트의 서빙 프로세스는 영향을 받지 않는다.
2. **Given** `llama_cpp.server` 모듈이 8081 포트에서 실행될 때, **When** `/health` 엔드포인트가 404를 반환하면, **Then** 즉시 `/v1/models` 엔드포인트를 폴백 조회하여 HTTP 200 OK 확인 시 정상 Readiness 통과로 처리한다.

---

### Edge Cases

- **모든 VRAM이 외부 프로세스에 의해 100% 점유된 경우**: 벤치마크 스크립트가 크래시 없이 "VRAM 부족으로 인한 측정 불가" 사유를 반환하고 안전하게 종료되는지 확인.
- **`--force-benchmark` 실행 중 사용자가 Ctrl+C (SIGINT)를 입력하는 경우**: 메인 서빙 서버 영향 없이 벤치마크 서브프로세스만 정리되고 안전 종료되는지 확인.
- **GGUF 모델 파일이 일부 손상되어 로딩 실패하는 경우**: 타 모델 벤치마크에 영향을 주지 않고 대상 모델만 실패 처리 후 다음 모델로 전환되는지 확인.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 백그라운드 서빙 서버 구동 상태에서 `uv run python scripts/benchmark_context_window.py --force-benchmark` 실행 시 메인 서빙 프로세스가 사살되거나 OOM으로 스크립트가 크래시되지 않음이 검증됨.
- **DoD-002**: 벤치마크 예외/실패 시 `model_context_profiles.json` 내 기존 정상 프로파일이 파괴되지 않고 안전 보존(Non-destructive)되는 로직 구현 및 단위 테스트 통과.
- **DoD-003**: `ProcessManager.force_kill_zombie_llama_servers()` 및 cleanup hook이 와일드카드 `pkill -9 -f llama-server` 대신 벤치마크 전용 포트/PID 타겟 기반 핀포인트 종료 방식으로 전환됨.
- **DoD-004**: `poll_server_health`에 `/v1/models` 폴백 조회 로직이 추가되어 `llama_cpp.server` 환경에서도 404 타임아웃 없이 정상 Readiness 검증 통과됨.
- **DoD-005**: 전체 파이썬 테스트 수트 (`uv run pytest`) 통과 및 회귀 검증 완료.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST 실시간 GPU 메모리 정보(NVML Free VRAM)를 측정하여 벤치마크 가용 VRAM 계산식에 적용해야 한다.
- **FR-002**: System MUST 백그라운드에 서빙 서버(`vllm_serv`)가 구동 중임을 감지할 경우 사용자에게 실행 시 경고 안내를 제공하거나 가용 자원 기준 사전 검증(Pre-flight Check)을 수행해야 한다.
- **FR-003**: System MUST 벤치마크 실행 시 생성한 특정 PID 및 바인딩 포트(예: 8081)의 서브프로세스만을 타겟팅하여 정리해야 하며, 다른 포트(8089, 8090, 8091 등)에서 구동 중인 서비스 프로세스에 영향을 주지 않아야 한다.
- **FR-004**: System MUST 벤치마크 실패 시 기존 `model_context_profiles.json`의 검증된 프로파일 기록을 유지하고, 실패한 실행 결과로 기존 정상 프로파일을 덮어쓰지(Destructive Overwrite) 않아야 한다.
- **FR-005**: System MUST 이진 탐색 벤치마크 실행 전 웜업 및 VRAM 한계점 계산 시 사전 한계 측정(Dry-run)과 실시간 VRAM 오버플로우 감지(T021)를 통해 CUDA OOM 발생 전에 프로세스를 안전 중단해야 한다.
- **FR-006**: System MUST CLI 인자로 `--keep-existing-profiles` 또는 덮어쓰기 방지 모드를 지원하여 안정적인 서빙 상태 유지를 보증해야 한다.
- **FR-007**: System MUST 벤치마크 결과 저장 시 원자적 파일 쓰기(Atomic File Write)를 적용하여 저장 도중 중단되어도 파일이 손상되지 않도록 보장해야 한다.
- **FR-008**: System MUST `poll_server_health` 수행 시 `/health` 엔드포인트 응답이 404인 경우(Python `llama_cpp.server` 구동 시) 즉시 `/v1/models` 엔드포인트를 폴백 조회하여 HTTP 200 OK 확인 시 서브프로세스 Readiness를 최종 승인해야 한다.

### Key Entities

- **ModelContextProfile**: 모델별 최대 검증 컨텍스트 크기, 권장 컨텍스트 크기, peak VRAM 사용량, TPS, 지원 여부(`is_supported`), 실패 사유(`failure_reason`), 테스트 시각 등의 정보를 담는 불변/원자적 엔티티.
- **GpuResourceSnapshot**: total_vram_mb, used_vram_mb, free_vram_mb 등 실시간 NVML 기반 GPU 자원 상태 스냅샷 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 벤치마크 실행 중 메인 서빙 서버(포트 8089/8090/8091)의 비의도적 프로세스 다운 발생 건수 0건.
- **SC-002**: 벤치마크 스크립트 비정상 종료/실패 발생 시 기존 프로파일 데이터 유실 비율 0%.
- **SC-003**: 가용 VRAM을 초과하는 컨텍스트 할당 시 커널 OOM Killer(Exit Code 137) 차단율 100% (사전 VRAM 한계 감지로 안전 거부).
- **SC-004**: `llama_cpp.server` 환경에서 `/health` 404 오진으로 인한 벤치마크 실패율 0%.
- **SC-005**: 전체 자동화 단위/통합 테스트 수트 (`uv run pytest`) 100% Pass.

## Assumptions

- 사용자는 NVIDIA GPU 및 NVML 드라이버 환경에서 파이썬 가상환경(`uv run`)을 통해 스크립트를 구동한다.
- 벤치마크 스크립트는 기본적으로 포트 8081을 임시 테스트 포트로 사용하며, 메인 인퍼런스 서버는 포트 8089, 임베딩은 8090, 리랭커는 8091을 사용한다.
- 벤치마크 실패 시 기존 검증 프로파일이 존재하는 경우 이전 프로파일을 보존하는 것이 무조건 2048 fallback 덮어쓰기보다 비즈니스적으로 유효하다.
