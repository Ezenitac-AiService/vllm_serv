# Feature Specification: 컨텍스트 윈도우 크기 벤치마킹 고도화 및 헬스체크/초기화 진단 개선 (105-enhance-context-window-benchmark)

**Feature Branch**: `105-enhance-context-window-benchmark`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "컨텍스트 윈도우 크기 벤치마킹 고도화를 했는데, 왜 저게 저렇게 되어있지? 대화 이력을 보고 구현 확인하고 스펙 작성해"

## Clarifications

### Session 2026-08-07

- Q: 고용량 컨텍스트 윈도우(`n_ctx` >= 5632) 실측 시 `llama-server` 초기화 시간에 비례한 헬스체크 타임아웃 및 스폰 파라미터 처리 방식은 무엇인가? → A: 고용량 `n_ctx` 설정 시 CUDA KV 캐시 메모리 할당 및 텐서 초기화에 소요되는 시간을 고려하여 `poll_server_health`의 타임아웃을 `n_ctx` 및 파일 크기에 따라 동적으로 확대(최대 60초)하고, 서브프로세스 초기화 실패 사유를 구체적으로 캡처한다.
- Q: 모델 카탈로그의 `default_n_ctx` 캡으로 인한 이진 탐색 구간 조기 종료 방지 지침은 무엇인가? → A: `default_n_ctx` (4096) 값에 의해 상한선이 고정되는 현상을 제거하고, 모델 카탈로그의 `max_n_ctx` (기본 16384) 또는 RoPE 최대 사양까지 실측 이진 탐색이 5단계(`range(5)`)에 걸쳐 진행되도록 탐색 알고리즘을 개선한다.
- Q: 벤치마크 결과 저장 시 `config/model_context_profiles.json` 프로필 유실 및 빈 프로필 덮어쓰기 방지 정책은 무엇인가? → A: `scripts/benchmark_quality.py` 및 `scripts/benchmark_context_window.py`에서 기존 프로필 데이터를 원자적으로 로드 및 병합(Merge)하여, 일부 모델 벤치마크 실패나 결과 미존재 시에도 기존에 검증된 12개 모델의 벤치마크 캐시가 훼손되지 않도록 보존한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 고용량 컨텍스트 윈도우 동적 탐색 및 헬스체크 타임아웃 적응형 확장 (Priority: P1)

시스템 운영자가 `python scripts/benchmark_context_window.py --force-benchmark` 또는 `--fine-grained`를 구동할 때, 소형/중형 모델의 이진 탐색이 4096 상한선에 갇히지 않고 16384까지 확장되며, 고용량 `n_ctx` (5632, 7168, 10240 등) 설정에 따른 `llama-server` 초기화 시간이 늘어나더라도 적응형 타임아웃(최대 60초)을 적용하여 오탐 타임아웃 실패 없이 실제 최대 성형 가용 컨텍스트 윈도우 크기를 정확하게 측정받아야 합니다.

**Why this priority**: 현행 이진 탐색 알고리즘은 `default_n_ctx: 4096` 캡과 짧은 헬스체크 타임아웃으로 인해 8192~16384 지원이 가능한 모델도 4096에 강제 고정되거나 `HEALTH_CHECK_TIMEOUT`으로 오탐되는 심각한 한계가 있으므로 최우선 개선이 필요합니다.

**Independent Test**: `uv run python scripts/benchmark_context_window.py --model qwen3.5-2b --fine-grained` 구동 시, 탐색 구간이 `[4096, 16384]`로 설정되고 동적 타임아웃 적용 하에 4096을 초과하는 유효 컨텍스트 크기(예: 8192 이상)가 정밀 측정되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 후보 모델의 이진 탐색이 구동될 때, **When** 모델 카탈로그의 `default_n_ctx`가 4096이더라도, **Then** 탐색 상한선은 `max_n_ctx` (기본 16384)로 자동 확장되어 `[4096, 16384]` 구간에서 5단계 이진 탐색이 정상 진행되어야 한다.
2. **Given** 고용량 `n_ctx` (예: 10240, 7168) 로딩 부하가 투입될 때, **When** `llama-server` 프로세스가 생성되면, **Then** KV 캐시 메모리 할당 시간에 맞추어 헬스체크 폴링 타임아웃이 동적으로 연장(최대 60초)되어 억억한 시간 초과 오탐을 방지해야 한다.

---

### User Story 2 - 원자적 프로필 캐시 병합 및 유실 방지 보존 메커니즘 (Priority: P2)

엔지니어 및 자동화 파이프라인이 품질 벤치마크(`benchmark_quality.py`) 또는 특정 모델 벤치마크를 구동할 때, 평가 결과가 비어 있거나 일부 모델만 측정되더라도 [config/model_context_profiles.json](file:///home/dev/storage/vllm_serv/config/model_context_profiles.json)의 기존 12개 서비스 모델 벤치마크 프로필이 `"profiles": {}`로 초기화되지 않고 안전하게 원자적 병합(Merge) 보존되어야 합니다.

**Why this priority**: 벤치마크 덮어쓰기 버그로 인해 기존에 실측 수록된 12개 모델의 컨텍스트 측정 캐시가 삭제되면 전체 서빙 설정 및 대시보드 조회가 마비되므로 안정성 확보가 필수적입니다.

**Independent Test**: 빈 벤치마크 결과(`reports=[]`)를 전달하여 `save_context_profiles_cache`를 호출할 때, `config/model_context_profiles.json`의 기존 12개 프로필이 훼손 없이 온전히 보존됨을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 벤치마크 파이프라인이 실행될 때, **When** 벤치마크 보고서 데이터가 존재하지 않거나 빈 리스트가 전달되면, **Then** 기존 `model_context_profiles.json` 파일을 유지하고 건너뛰는 로그를 출력하며 파일을 초기화하지 않아야 한다.
2. **Given** 일부 모델에 대해서만 신규 벤치마크가 수행될 때, **When** 결과를 프로필 캐시에 저장하면, **Then** 기존 측정된 다른 모델들의 데이터와 원자적으로 병합(Merge)되어 저장되어야 한다.

---

### User Story 3 - 벤치마크 진단 로그 및 정밀 오류 원인 추적성 강화 (Priority: P3)

운영자가 벤치마크 수행 중 타임아웃, VRAM 초과, C++ 인퍼런스 에러 등 failure가 발생한 모델의 상세 내역을 조회할 때, 단순히 `Supported: False` 외에 실측 시 시도한 `n_ctx` 단계별 상세 기록과 백엔드 파이프 실패 원인(OOM, Timeout, Allocation Error)이 `logs/benchmark.log` 및 `model_context_profiles.json` 내 `binary_search_steps`에 투명하게 상술되어야 합니다.

**Why this priority**: 개발자 및 SRE가 수치가 왜 낮은지, 특정 `n_ctx`에서 왜 실패했는지 원인을 빠르게 진단하고 시스템 파라미터를 조정할 수 있도록 투명한 관찰 가능성을 제공합니다.

**Independent Test**: 실패가 발생한 모델 평가 후 `config/model_context_profiles.json`을 조회하여 `binary_search_steps` 항목에 시도된 `n_ctx`, 실측 VRAM 사용량, failure_reason이 정확하게 기록되어 있는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 벤치마크 이진 탐색 중 특정 `n_ctx` 테스트가 실패할 때, **When** 탐색 결과를 덤프하면, **Then** `binary_search_steps` 배열에 각 단계별 `tested_n_ctx`, `status` ("PASS" 또는 "OOM/FAIL"), `reason`이 명확히 기록되어야 한다.

---

### Edge Cases

- `n_ctx=16384` 설정 시 물리 GPU VRAM (11,264MB)의 92%를 초과하는 경우: 안전을 위해 CUDA OOM 예방 트래핑으로 해당 단계를 실패 처리하고 이전의 안정적인 `n_ctx`를 최적값으로 확정합니다.
- `llama-server` 서브프로세스가 커널 OOM Killer(SIGKILL/Exit Code 137)로 강제 종료되는 경우: 예외를 포착하여 "CUDA_OOM_KILLED (Process terminated by SIGKILL)" 사유로 명시 기록합니다.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/benchmark_context_window.py`에서 `default_n_ctx` 캡을 해제하고 `[4096, 16384]` 상한 탐색 및 5단계 이진 탐색이 정상 동작함을 단위/통합 테스트로 입증한다.
- **DoD-002**: `poll_server_health`의 동적 타임아웃(최대 60초)을 적용하여 고용량 `n_ctx` 설정 시 초기화 타임아웃 오탐이 발생하지 않음을 실측 검증한다.
- **DoD-003**: `scripts/benchmark_quality.py`의 `save_context_profiles_cache` 원자적 병합(Merge) 로직을 적용하여 빈 결과 수신 시 캐시 유실이 없음을 검증한다.
- **DoD-004**: `uv run pytest` 전체 회귀 테스트 수트가 100% Green Pass를 달성한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST uncap the binary search context upper limit from `default_n_ctx` (4096) to `max_n_ctx` (default 16384) to allow discovering high-capacity context windows for supported models.
- **FR-002**: System MUST scale `llama-server` health polling timeouts dynamically (up to 60 seconds) based on `n_ctx` allocation size and model size to prevent false-positive health check timeouts during server initialization.
- **FR-003**: System MUST atomically load and merge context profile updates into `config/model_context_profiles.json` and MUST NOT overwrite existing valid profile entries with empty records when benchmark outputs are empty.
- **FR-004**: System MUST perform up to 5 binary search steps (`range(5)`) per model with 512-token block alignment to achieve high precision context window optimization.
- **FR-005**: System MUST log detailed step-by-step trial history (`binary_search_steps`), VRAM utilization, and specific failure reasons (OOM, Timeout, Exit Code) in both `logs/benchmark.log` and profile cache metadata.

### Key Entities

- **ModelContextProfile**: `config/model_context_profiles.json`에 저장되는 모델별 컨텍스트 프로필 엔티티 (`max_context_length`, `recommended_context_length`, `binary_search_steps`, `peak_vram_mb`, `tpot_tok_per_sec`, `scaling_tested`, `is_supported`, `failure_reason`, `last_tested_at`).
- **BinarySearchStep**: 단일 이진 탐색 시도 엔티티 (`step`, `tested_n_ctx`, `real_vram_mb`, `status`, `reason`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `qwen3.5-2b` 및 `gemma4-e2b` 등 소형 모델의 컨텍스트 윈도우 탐색 상한선이 4096에서 16384로 확장되어 실측 최고 가용 윈도우 크기가 탐색된다.
- **SC-002**: 고용량 `n_ctx` 로딩 시 헬스체크 타임아웃 오탐률이 0%로 감소한다.
- **SC-003**: 벤치마크 예외/비정상 종료 시에도 `config/model_context_profiles.json` 내 기존 12개 프로필 유실률 0%를 보장한다.
- **SC-004**: 전체 파이썬 회귀 테스트 수트(`uv run pytest`) 통과율 100%를 달성한다.

## Assumptions

- 타겟 레퍼런스 GPU인 NVIDIA GeForce GTX 1080 Ti (11,264MB VRAM) 기준 가용 메모리 상에서 최적 컨텍스트 크기를 탐색합니다.
- `llama-server` 백엔드는 Flash Attention 및 GQA 모드를 활용하여 KV 캐시 메모리 사용을 효율화합니다.
- `config/model_catalog.json`의 모델 메타데이터를 기반으로 기본 파라미터를 추론합니다.
