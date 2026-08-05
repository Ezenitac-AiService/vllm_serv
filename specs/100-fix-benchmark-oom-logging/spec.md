# Feature Specification: 벤치마크 OOM 진단 및 실시간 로그 영구 저장 개선 (100-fix-benchmark-oom-logging)

**Feature Branch**: `100-fix-benchmark-oom-logging`

**Created**: 2026-08-05

**Status**: Draft (Remediated with Smart Skip Catalog Reconciliation & Multi-Persona Improvements)

**Input**: User description: "벤치마크 결과가 납득되지 않음. 죄다 oom이야, 이건 벤치마크중 오류가 발생한것 같은데? setup.sh의 파이프라인중 벤치마크는 로그를 남기나? /home/dev/storage/vllm_serv/logs 로그도 확인해보고..."

## Clarifications

### Session 2026-08-05

- Q: 11GB VRAM (GTX 1080 Ti) 환경에서 9B 및 12B 모델의 탑재 가능 여부 및 이진 탐색 최적화 기준은 무엇인가? → A: 11GB VRAM 환경에서 9B 및 12B 모델은 소형 컨텍스트(2048~4096) 수준에서 정상 가동되어야 하므로, 고용량 n_ctx(10240 등) 시도로 인한 사전 차단(CUDA OOM Risk) 대신 모델 크기별 적합한 n_ctx 초기값(2048 또는 4096)부터 이진 탐색을 개시하여 오탐을 방지한다.
- Q: 하드웨어 모델명(GTX 1070, GTX 1080 Ti 등) 및 특정 모델 크기(12B, 9B 등)에 대한 코드 내 하드코딩 조건 분기가 허용되는가? → A: 전면 금지함. 후보 모델 카탈로그 및 GPU 장비 변경 시 유연성을 보장하기 위해 하드웨어 명칭이나 특정 모델 ID 하드코딩 분기(if-else)를 완전히 제거하고, `config/model_catalog.json`의 모델 메타데이터(GGUF 파일 크기/파라미터) 및 실시간 GPU VRAM 측정값(`get_nvml_vram_info()`)에 기반하여 KV 캐시 용량 및 이진 탐색 시작 구간(`n_ctx`)을 동적으로 산출하는 100% 데이터 기반(Data-Driven) 메커니즘을 적용한다.
- Q: setup.sh 및 벤치마크/프로비저닝 파이프라인 전반에서 전면 제거해야 할 추가 하드코딩 및 회피(Fallback) 로직은 무엇인가? → A: 파이프라인 전반에 잔존하는 5개 하드코딩/회피 로직(`REQUIRED_MODELS` 정적 배열, `"2b"` 문자열 탐색, `2600+0.4*mid` 가짜 수식, `"legacy-i7-930"` 휠 매칭, `vram_est_mb=6000` 기본 정적 폴백)을 전면 제거하고 100% 동적 메타데이터 기반으로 정제한다.
- Q: 다중 페르소나 분석에서 적발된 4대 SRE/런타임 보완점(Exit Code 137 처리, 500MB VRAM 안전 버퍼, 디스크 로그 로테이션, 파이프 EOF 클로즈)의 반영 지침은 무엇인가? → A: 커널 OOM Killer 강제 종료(Exit Code 137/-9) 감지 메커니즘 수록, 가용 VRAM 계산 시 CUDA Context 변동성에 대응하기 위한 500MB 안전 버퍼 확보, `logs/benchmark.log` 10MB 초과 시 원자적 로테이션, 프로세스 강제 종료 시 파이프 EOF 피딩을 통한 안전 플러시를 명세에 반영함.
- Q: Hugging Face / ModelScope 가중치 신규 다운로드뿐만 아니라 이미 로컬에 모델 가중치가 존재(Smart Skip)할 때의 `config/model_catalog.json` 실측 정보 동기화 지침은 무엇인가? → A: `ensure_models.py` / `ModelDownloader`가 모델 가중치 신규 다운로드를 완납하는 시점뿐만 아니라, 이미 파일이 로컬에 존재하여 다운로드를 스마트 스킵(Smart Skip)하는 시점에도 `os.path.getsize(model_path)`를 실행하여 카탈로그의 `exact_bytes` 및 `size_gb` 정보가 최신 실측값과 일치하도록 자율 동기화(Reconciliation)한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 벤치마크 서브프로세스 실시간 로그 영구 저장 및 추적성 확보 (Priority: P1)

시스템 관리자가 `./setup.sh --force-benchmark` 또는 벤치마크 평가를 실행할 때, 각 후보 모델의 실측 인퍼런스 및 이진 탐색 과정에서 발생한 `llama-server` 백엔드의 표준 출력(stdout) 및 표준 에러(stderr)가 실시간으로 파일로그(`logs/benchmark.log` 및 `logs/error.log`)에 누적 기록되어 타임아웃, CUDA OOM, C++ 예외 발생의 근본 원인을 투명하게 추적할 수 있어야 합니다.

**Why this priority**: 현재 벤치마크 수행 시 백엔드 서브프로세스의 로그 출력이 스트림 캡처 과정에서 유실되어, 모델 획득/로딩/VRAM 부족 시 구체적 실패 원인을 파악할 방법이 없으므로 최우선 개선이 필요합니다.

**Independent Test**: `./setup.sh --force-benchmark` 실행 중 `tail -f logs/benchmark.log` 또는 `logs/error.log`를 통해 각 모델별 로딩 시도, CUDA buffer 할당 상태, exit code 및 타임아웃 사유가 실시간 저장됨을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 벤치마크 파이프라인이 구동 중일 때, **When** 특정 모델의 `llama-server` 인스턴스가 생성되면, **Then** 표준 출력 및 에러 출력이 `logs/benchmark.log` 파일에 실시간 캡처 및 추가 기록되어야 한다.
2. **Given** 벤치마크 중 프로세스 종료(SIGKILL/SIGTERM) 또는 타임아웃이 발생할 때, **When** 벤치마크 종료 후 로그 파일을 확인하면, **Then** 마지막 20줄 이상의 콘솔 출력 및 비정상 종료 사유가 `logs/error.log` 및 `logs/benchmark.log`에 보존되어야 한다.

---

### User Story 2 - 동적 데이터 기반 VRAM 산정식, 500MB 안전 버퍼 및 헬스체크 타임아웃 최적화 (Priority: P2)

엔지니어 및 개발자가 다양한 규격의 후보 모델들에 대해 `--force-benchmark`를 수행할 때, 특정 하드웨어명이나 모델 ID 하드코딩 없이 동적 메타데이터 기반 VRAM 계산(500MB 안전 쿠션 확보) 및 동적 헬스체크 타임아웃을 통해 지원 가능한 모델들이 타임아웃이나 잘못된 사전 차단(CUDA OOM Risk) 없이 올바르게 평가받을 수 있어야 합니다.

**Why this priority**: 10초 고정 타임아웃 및 하드코딩된 정적 VRAM 산정 방식은 가용 물리 VRAM 내에서 정상 동작 가능한 모델조차 "timed out" 또는 "OOM Risk"로 잘못 판정하게 만듭니다.

**Independent Test**: 카탈로그 내 다양한 모델에 대해 하드코딩 분기 없이 동적 VRAM 예측 및 동적 헬스체크 타임아웃(최대 30초)을 적용하여, 이진 탐색이 정상 수행되어 유효 TPS 및 컨텍스트 크기 프로파일이 생성되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** GGUF 모델 가중치를 GPU VRAM으로 로딩하는 단계에서, **When** 대형 모델 초기화에 10초 이상 소요되더라도, **Then** 동적 헬스체크 타임아웃(최대 30초 내) 동안 대기하여 오탐으로 인한 이진 탐색 실패를 방지해야 한다.
2. **Given** 임의의 물리 GPU VRAM 용량 환경에서, **When** 카탈로그 모델의 메타데이터 기반으로 이진 탐색 구간을 설정할 때, **Then** 500MB 안전 VRAM 버퍼를 남긴 가용 메모리 상에서 안전한 초기 탐색 구간(`n_ctx`)을 동적으로 산출해야 한다.

---

### User Story 3 - 벤치마크 결과 프로필 저장, 커널 OOM 캡처, 카탈로그 동기화 및 정밀 실패 사유 피드백 (Priority: P3)

운영자가 벤치마크 완료 후 `config/model_context_profiles.json` 프로필 및 콘솔 출력을 조회할 때, 단순 `Supported: False`가 아닌 구체적인 실패 사유(Kernel OOM Killer, Timeout, File Missing)와 함께 실제 성공한 모델 중 최적의 서빙 모델이 올바르게 자동 선정되어 반영되어야 하며, 모델 다운로드 완료 또는 기존 파일 존재(Smart Skip) 시 `config/model_catalog.json`의 실측 용량 메타데이터가 자율 동기화되어야 합니다.

**Why this priority**: 지원 가능한 모델이 하나 이상 있음에도 불구하고 벤치마크 실패로 인해 잘못된 최적 모델 선정이나 TPS `-1.0` 기본값으로 복구되는 현상을 막고 최종 서비스 정합성을 보장합니다.

**Independent Test**: 전체 후보 모델 평가 완결 후 `config/model_context_profiles.json`에 모델별 상세 결과(binary_search_steps, failure_reason, TPS, VRAM)가 기록되고 `config/model_catalog.json`의 실측 파일 크기가 업데이트됨을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 전체 후보 LLM 모델 실측 평가 완결 시, **When** 지원 가능한 모델이 존재하는 경우, **Then** 가장 높은 TPS 및 안정적 VRAM을 기록한 유효 모델이 최적 서빙 모델로 선정되어야 한다.
2. **Given** 커널 OOM Killer(Exit Code 137/-9) 등에 의한 강제 종료 발생 시, **When** 프로파일 json 데이터를 저장할 때, **Then** failure_reason에 "KERNEL_OOM_KILLER_EXIT_137" 등 구체적 진단 원인이 수록되어야 한다.
3. **Given** Hugging Face/ModelScope 다운로드 완료 또는 기존 로컬 파일 감지(Smart Skip) 시, **When** 모델 파일의 존재를 확인하면, **Then** `config/model_catalog.json` 내 해당 모델의 `size_gb` 및 `exact_bytes` 필드가 로컬 가중치 실측값으로 원자적 자율 동기화(Reconcile)되어야 한다.

---

### User Story 4 - 벤치마크 로그 파일 로테이션 및 디스크 안정성 보장 (Priority: P4)

벤치마크를 반복 실행할 때 `logs/benchmark.log` 파일의 무한 증폭으로 인한 디스크 고갈을 방지하도록 10MB 초과 시 자동 로테이션을 수행합니다.

**Why this priority**: 지속적 벤치마크 및 CI/CD 환경에서 디스크 공간 고갈 문제를 사전 예방합니다.

**Independent Test**: `logs/benchmark.log` 파일 용량이 10MB를 초과할 경우 `logs/benchmark.log.old`로 원자적 이동(rotate) 후 신규 로그 파일이 생성됨을 확인합니다.

---

### Edge Cases

- 백엔드 서브프로세스가 커널 OOM Killer(Exit Code 137, SIGKILL -9)에 의해 즉시 살해되어 stderr 출력이 없을 때 "KERNEL_OOM_KILLER_EXIT_137" 메시지를 `logs/error.log` 및 프로필에 수록하는가?
- `logs/benchmark.log`가 10MB를 초과할 때 이전 로그가 `logs/benchmark.log.old`로 로테이션되는가?
- 벤치마크 도중 사용자가 Ctrl+C로 강제 중단했을 때 파이프 EOF를 피딩하여 잔여 로그 스트림을 안전 플러시한 후 닫는가?
- 모델 파일이 이미 로컬에 존재하여 다운로드가 스마트 스킵(Smart Skip)되더라도 `config/model_catalog.json` 내 `exact_bytes`와 `size_gb`가 실측값으로 정상 보정되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `./setup.sh --force-benchmark` 실행 시 모든 후보 모델의 `llama-server` 인스턴스 로그가 `logs/benchmark.log` 및 `logs/error.log`에 명확히 영구 기록되는 벤치마크 파이프라인 구현 및 검증.
- **DoD-002**: 하드웨어/모델명 하드코딩 없이 100% 동적 메타데이터 기반 VRAM 예산 산정(500MB 안전 버퍼 포함) 및 동적 헬스체크 타임아웃(최대 30초)을 적용하여 이진 탐색 오탐을 방지하고 정상 측정 결과를 도출함을 실측 검증.
- **DoD-003**: Exit Code 137(Kernel OOM Killer) 감지 진단 수록, `logs/benchmark.log` 10MB 로테이션, 5대 잔존 하드코딩 철거 및 다운로드/스마트스킵 시 `model_catalog.json` 실측 메타데이터 자율 동기화(`FR-012`) 완납.
- **DoD-004**: 벤치마크 관련 단위/통합 테스트 수트 (`uv run pytest`) 100% Pass 및 헌장 원칙(하드코딩 금지, Fake Green 금지, 한국어 소통, 영문 추론) 준수.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST 벤치마크 파이프라인 실행 중 각 서브프로세스(`llama-server`)에서 발생하는 모든 stdout/stderr 로그를 `logs/benchmark.log` 파일에 실시간 스트리밍 기록해야 한다.
- **FR-002**: System MUST 벤치마크 서브프로세스가 비정상 종료(exit code != 0)되거나 타임아웃 발생 시, 최근 20줄 이상의 백엔드 로그 덤프를 `logs/error.log` 및 `logs/benchmark.log`에 보존하고 벤치마크 프로필에 구체적 에러 메시지를 기록해야 한다.
- **FR-003**: System MUST 벤치마크 헬스체크 대기 시간(polling timeout)을 기존 고정 10초에서 모델 초기화 시간 및 크기에 따라 가변 대기(최대 30초)하도록 확대 조정해야 한다.
- **FR-004**: System MUST 하드웨어 명칭(GTX 1070, 1080 Ti 등)이나 특정 모델 ID/규모(9B, 12B 등)의 하드코딩 예외 조건문을 전면 제거하고, `config/model_catalog.json` 메타데이터 및 동적 NVML GPU VRAM 실측값에 기초하여 이진 탐색 초기 `n_ctx` 범위와 KV 캐시 VRAM 예산을 동적으로 산출해야 한다.
- **FR-005**: System MUST 벤치마크 중 프로세스 강제 종료(`stop_process`)가 일어날 때, 파이프 EOF 피딩 및 안전 수거 메커니즘을 통해 백그라운드 로그 스트림 드레인 루프에 남은 잔여물이 유실되지 않도록 보장해야 한다.
- **FR-006**: System MUST 벤치마크 완료 후 `config/model_context_profiles.json` 프로필 파일에 모델별 실패 사유(`failure_reason`) 및 측정 단계별 상태를 명확히 기록하여 대시보드 및 CLI에서 진단 가능하도록 보장해야 한다.
- **FR-007**: System MUST `ensure_models.py` 및 `setup.sh`에 정적으로 지정되어 있던 `REQUIRED_MODELS` 배열 및 `"legacy-i7-930"` 하드코딩 조건문/경로를 삭제하고, `config/server_config.json` 및 `config/model_catalog.json` 카탈로그와 `cpu_detector` 프로파일 매칭 결과로부터 필수 모델 목록 및 `$MATCHED_PROFILE` 기반 휠 경로를 동적으로 탐색해야 한다.
- **FR-008**: System MUST `benchmark_context_window.py` 및 `ProcessManager` 내 잔존하는 가짜 정적 산정식(`2600 + int(mid * 0.4)` 및 `vram_est_mb = 6000` 기본값)을 전면 제거하고 GGUF 가중치 용량 및 NVML VRAM 실측 델타 기반 정밀 산출 모듈로 전면 교체해야 한다.
- **FR-009**: System MUST 커널 OOM Killer 등에 의해 exit code가 137 또는 -9로 강제 종료될 경우, 이를 명확히 감지하여 `failure_reason`에 "KERNEL_OOM_KILLER_EXIT_137" 진단 문구를 명시 기록해야 한다.
- **FR-010**: System MUST 동적 VRAM 예산 산출 시 CUDA Context 및 드라이버 오버헤드 변동성에 대응할 수 있도록 가용 VRAM에서 최소 500MB의 안전 버퍼(Safety Cushion)를 차감한 가용 용량(`Usable VRAM = Total VRAM - 500MB`)을 기준으로 이진 탐색을 구동해야 한다.
- **FR-011**: System MUST 벤치마크 개시 시 `logs/benchmark.log` 파일 용량을 검사하여 10MB 초과 시 `logs/benchmark.log.old`로 원자적 로테이션하여 디스크 고갈을 방지해야 한다.
- **FR-012**: System MUST `ensure_models.py` / `ModelDownloader`에서 모델 다운로드 완납 시점뿐만 아니라 로컬 파일 존재 확인(Smart Skip) 시점에도, 실제 로컬 GGUF 파일의 정밀 용량(Bytes/GB)을 측정하여 `config/model_catalog.json` 내 해당 모델 항목의 `size_gb` 및 `exact_bytes` 필드에 원자적으로 동기화(Reconcile)해야 한다.

### Key Entities

- **BenchmarkExecutionLog**: 벤치마크 실행 시 모델명, 탐색 단계(n_ctx), 타임스탬프, 종료 코드, 캡처된 서브프로세스 출력, 실패 원인을 포함하는 로그 데이터 구조.
- **ModelContextProfile**: 후보 모델별 최대 컨텍스트, 권장 컨텍스트, peak VRAM, TPS, 지원 여부(is_supported), 구체적 실패 사유(failure_reason)가 기록되는 JSON 엔티티.
- **ModelCatalogItem**: 모델 ID별 리포지토리 ID, 파이프라인 분류, 로컬 가중치 경로, 로컬 스토리지 실측 파일 용량(`exact_bytes`, `size_gb`) 및 설정 메타데이터 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./setup.sh --force-benchmark` 실행 후 `logs/benchmark.log` 파일에 100% 벤치마크 실행 기록 및 모델별 백엔드 출력이 저장되어 로그 유실율 0% 달성.
- **SC-002**: 물리 GPU VRAM 상에서 500MB 안전 버퍼를 갖춘 동적 이진 탐색을 통해 가용 로컬 모델들이 헬스체크 타임아웃 오탐 없이 정상 측정을 통과하여 유효 TPS 및 컨텍스트 크기 도출.
- **SC-003**: 5대 잔존 하드코딩 제거, Exit Code 137 커널 OOM Killer 감지, `logs/benchmark.log` 10MB 로테이션 및 신규 다운로드/Smart Skip 시 `model_catalog.json` 실측 메타데이터 자율 동기화(`FR-012`) 100% 정상 작동함.
- **SC-004**: 프로젝트 전체 회귀 테스트 수트 (`uv run pytest`) 100% Pass.

## Assumptions

- 벤치마크 대상 시스템은 NVIDIA GPU 및 CUDA 가속 지원 환경을 갖추고 있다.
- `logs/` 디렉토리에 파일 쓰기 권한이 보장되어 있다.
- 후보 GGUF 모델 가중치가 `models/` 디렉토리에 정상 존재하거나 자동 다운로드 파이프라인에 의해 접근 가능하다.
