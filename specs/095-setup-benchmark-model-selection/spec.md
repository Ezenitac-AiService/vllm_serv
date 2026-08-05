# Feature Specification: `setup.sh` 4단계 모듈화 파이프라인(다운로드/검증/컨텍스트 윈도우 벤치마크/설정 반영)을 통한 최적 서비스 모델 및 컨텍스트 크기 자동 선정 (`095-setup-benchmark-model-selection`)

**Feature Branch**: `095-setup-benchmark-model-selection`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "setup.sh를 한단계 더 고도화 해야 할것 같아. 스크립트 중에, 벤치마크를 통해, 플렛폼에서 서비스할 모델 선정, 모델의 컨텍스트 윈도우 크기 기준을 선정하는 uv run python scripts/benchmark_quality.py --auto-download --real 이게 setup 과정에 있어야 타당하지 않나? 해당 스크립트를 그냥 호출하지 말고, 기능을 쪼개서, 모델 다운로드하는 로직, 검증하는 로직, 서비스를 시작하고 컨텍스트 윈도우 벤치마크를 통해 서비스할 모델 선정, 컨텍스트 윈도우 크기 결정 -> 설정 파일에 반영 하도록 분해 하는게 나을거 같아"

## Clarifications

### Session 2026-08-04

- Q: setup.sh 내 벤치마크 모듈화 4단계 파이프라인 분해 정책 → A: Option A (다운로드 / 검증 / 임시 서빙 & 컨텍스트 윈도우 벤치마크 / 선정 & 설정 반영 4단계 분해 파이프라인 spec.md 반영)

### Session 2026-08-05

- Q: 컨텍스트 윈도우 크기 한계를 측정하는 벤치마크가 2배씩 올라가는 것(2K, 4K, 8K, 16K)이 타당한가? → A: 타당함. LLM 트랜스포머 아키텍처의 KV 캐시 메모리 소모는 컨텍스트 길이($N_{ctx}$)에 비례하며, RoPE 및 토크나이저의 표준 규격이 2의 거듭제곱($2^n$) 단위로 정렬되므로 2배 단위(2048, 4096, 8192, 16384) 단계별 오프셋 측정이 가장 효율적이고 타당함.
- Q: 8GB/11GB/12GB 등 고정 VRAM 환경에서 2K~32K 간격 사이의 미세 컨텍스트(5K, 6K, 10K, 12K, 20K) 정밀 판정 정책 → A: Option A (Two-Pass Refinement Strategy). 기본 setup.sh는 2배 간격(2K, 4K, 8K, 16K)으로 고속 판정하며, 오프라인/마이그레이션 정밀 프로파일링 구동 시(`--fine-grained`) 상한 구간과 실패 구간 사이의 중간 오프셋(예: 10K, 12K)을 2차 탐색하여 `config/model_context_profiles.json`에 정밀 보존함.
- Q: 2차 심층 탐색 시 컨텍스트 윈도우 크기 탐색 방법론 및 트랜스포머 스케일링 정합성 → A: Option A (Binary Search with 512/1024 Block Alignment & RoPE Cap). 트랜스포머 KV 캐시 블록 및 GGML/vLLM SIMD 텐서 얼라인먼트에 맞추어 탐색 단위를 1024/512 토큰 배수(`multipleOf: 512`)로 엄격 정렬하고, 물리 OOM 상한과 모델별 RoPE 최대 지원 길이의 최소값(`min(physical_max, model_max_rope)`)으로 안전 캡을 적용함.
- Q: setup.sh 셋업 파이프라인에서 실제 벤치마킹 기반 모델 선정 및 실측 이진 탐색 컨텍스트 크기 결정 폴리싱 구조 → A: setup.sh가 실측 GPU 인퍼런스 및 실측 GPU 이진 탐색(Real GPU Process Spawning Binary Search)을 거쳐 OOM 경계를 찾고 정밀 컨텍스트 윈도우 크기를 결정하여 server_config.json 및 model_context_profiles.json을 최종 반영 후 서버 셋팅을 완수하는 파이프라인으로 전면 정립.
- Q: setup.sh 호출 대상 스크립트 폴리싱 및 불용 파일 정리 정책 → A: setup.sh가 호출하는 연동 하위 스크립트들(`ensure_models.py`, `benchmark_context_window.py`, `start_server.sh`, `stop_server.sh`, `status_server.sh` 등)의 경로 분기 및 오류 처리를 함께 폴리싱하고, 용도가 상실된 불용/만료 파일들을 검토 정리함.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - `setup.sh` 4단계 모듈화 파이프라인을 통한 서빙 모델 및 컨텍스트 윈도우 자동 선정 (Priority: P1) 🎯 MVP

시스템 관리자 및 AI 엔지니어는 플랫폼 마이그레이션 또는 셋업을 위해 `./setup.sh`를 실행할 때, 통으로 통합된 벤치마크 스크립트를 무작정 호출하는 대신 4가지 명확한 모듈식 단계(1. 모델 다운로드, 2. 파일 무결성 검증, 3. 임시 서빙 가동 및 컨텍스트 윈도우 벤치마크, 4. 서비스 모델 및 컨텍스트 크기 결정 & 설정 반영)로 순차 실행되어 호스트 하드웨어(CPU/GPU/VRAM)에 최적화된 서빙 모델과 컨텍스트 윈도우 기준 크기를 정밀 판정·선정하여 `config/server_config.json`에 반영하기를 원한다.

**Why this priority**: 단순 통 스크립트 실행은 단계별 실패 원인 추적이 어렵고 VRAM 소모 파악이 불투명하므로, 프로비저닝/검증/컨텍스트 실측/설정 반영의 4단계로 분해하여 투명성과 디버깅 용이성을 확보해야 한다.

**Independent Test**: `./setup.sh` 구동 시 4개 모듈식 단계가 순차 호출되고, 3단계 임시 가동 컨텍스트 측정 결과에 따라 `config/server_config.json`에 최적 모델 및 컨텍스트 윈도우 크기가 자동 업데이트되는지 검증.

**Acceptance Scenarios**:

1. **Given** 플랫폼 호스트에서 `./setup.sh`를 실행할 때, **When** 컴파일 환경 준비가 완료되면, **Then** 1단계(모델 다운로드: `ensure_models.py`)와 2단계(GGUF 무결성 검증)가 완수된다.
2. **Given** 모델 무결성 검증이 완료되었을 때, **When** 3단계(임시 서빙 가동 및 컨텍스트 윈도우 벤치마크)가 구동되면, **Then** 후보 모델별 컨텍스트(2K, 4K, 8K, 16K) 단계적 오프셋 실측 VRAM 및 TPS가 측정된다.
3. **Given** 3단계 실측 측정이 완료되었을 때, **When** 4단계(선정 & 설정 반영)가 실행되면, **Then** 결정된 최적 모델과 컨텍스트 윈도우 크기가 `config/server_config.json`에 자동 저장된다.

---

### User Story 2 - 빠른 셋업 및 CI/CD를 위한 벤치마크 스킵 옵션 지원 (Priority: P2)

운영 관리자 및 자동화 파이프라인은 빠른 서버 가동 또는 CI/CD 테스트 환경에서 `./setup.sh --skip-benchmark` 플래그를 사용하여 벤치마크 실행 시간을 절약하고 기존 프로파일 기본 설정으로 고속 셋업을 완료하기를 원한다.

**Independent Test**: `./setup.sh --skip-benchmark` 구동 시 3단계 벤치마크 수행을 스킵하고 기존 `config/server_config.json` 설정을 보존한 채 15초 이내에 셋업이 완수되는지 검증.

**Acceptance Scenarios**:

1. **Given** 개발자나 자동화 파이프라인이 `./setup.sh --skip-benchmark`를 구동할 때, **When** 셋업 단계에 도달하면, **Then** 3단계 벤치마크 측정을 스킵하고 `config/server_config.json`의 기존 `context_window` 설정값을 유지한 채 15초 이내 고속 완료한다.

---

### User Story 3 - 벤치마크 하드코딩/목업 제거 리팩토링 및 2단계 이진 탐색 정밀 프로파일링 (Priority: P3)

시스템 관리자 및 AI 아키텍트는 벤치마크 스크립트(`scripts/benchmark_quality.py`, `scripts/benchmark_context_window.py`) 내 하드코딩된 베이스라인 상수, 가짜 비율 계산(`* 0.2`), 회피성 목업 로직을 제거하고, NVML 실제 GPU VRAM 수집 및 2단계 이진 탐색(Binary Search, 최소 1024 해상도) 모드를 도입하여 `config/model_context_profiles.json` 및 `data/reports/analysis_report_quality.md`에 실측 정밀 프로파일을 기록하기를 원한다.

**Independent Test**: `python scripts/benchmark_context_window.py --fine-grained` 구동 시 하드코딩 값 없이 NVML/API 실측 텔레메트리로 2단계 이진 탐색을 구동하여 1024 단위 정밀 한계 컨텍스트 크기를 `config/model_context_profiles.json`에 저장하는지 검증.

**Acceptance Scenarios**:

1. **Given** 오프라인 마이그레이션 또는 정밀 프로파일링 시, **When** `benchmark_context_window.py --fine-grained`를 구동하면, **Then** 1차 2배 스케일링 구간 $[C_{pass}, C_{fail}]$에 대해 1024(1K) 해상도의 이진 탐색을 거쳐 실측 최적 상한 컨텍스트를 `config/model_context_profiles.json`에 기록한다.
2. **Given** 벤치마크 품질/성능 보고서 생성 시, **When** `benchmark_quality.py`가 실행되면, **Then** 가짜 상수에 의존하지 않고 NVML GPU 텔레메트리 및 API 실측 결과 기반으로 보고서를 작성한다.

---

### User Story 4 - `setup.sh` 연동 하위 스크립트 전면 폴리싱 및 불용 파일 정리 (Priority: P3)

시스템 관리자 및 유지보수 엔지니어는 `setup.sh` 파이프라인이 호출하는 연동 하위 스크립트들(`scripts/ensure_models.py`, `scripts/benchmark_context_window.py`, `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh` 등)의 예외 처리, 비대화형 흐름, 경로 분기가 정밀 폴리싱되고, 용도가 상실되거나 만료된 불용 스크립트/임시 파일이 정돈되어 깨끗하고 안정적인 스크립트 구조를 유지하기를 원한다.

**Independent Test**: `setup.sh` 구동 시 연동 스크립트 간 예외 없이 원활히 파이프라인이 완료되며, 정리된 불용 스크립트 없이 필수 모듈만 순수 가동되는지 검증.

**Acceptance Scenarios**:

1. **Given** `setup.sh` 구동 시, **When** 하위 셋업 스크립트를 순차 호출할 때, **Then** 예외 경로나 파일 누락 없이 100% 모듈화되어 정상 수행된다.
2. **Given** 셋업 파이프라인 리팩토링 시, **When** 불용/만료 파일 정리가 구동되면, **Then** 중복되거나 용도가 상실된 스크립트를 정돈하여 명확한 유지보수성을 보존한다.

---

## Edge Cases & Error Handling *(mandatory)*

- 3단계 벤치마크 도중 GPU 메모리 부족(OOM) 또는 예외 발생 시: `[BENCHMARK WARN]` 경고를 출력하고 안전 기본 프로파일(qwen3.5-4b, 4096 context)로 안전 폴백하여 `setup.sh` 실행 중단 방지.
- 비대화형(CI/CD) 환경에서 벤치마크 실행 시: 자동 타임아웃(예: 120초)을 설정하여 무한 대기 방지.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `setup.sh` 내 4단계 모듈화 파이프라인(1. 다운로드, 2. `verify_model_integrity` 실체적 검증, 3. 임시 서빙 & 컨텍스트 벤치마크, 4. 선정 & 설정 반영) 구현 완료
- **DoD-002**: 실측 컨텍스트 윈도우 결과 기반 서빙 모델 및 컨텍스트 윈도우 크기 자동 결정 및 `config/server_config.json` 원자적 업데이트 연동 완료
- **DoD-003**: `--skip-benchmark` 플래그 및 4단계 모듈식 셋업 연동 단위/통합 테스트 수트 (`tests/unit/test_setup_benchmark_integration.py`) 100% 통과 입증
- **DoD-004**: 벤치마크 스크립트 내 하드코딩/목업/회피 로직 제거 리팩토링 및 2단계 이진 탐색(`--fine-grained`) 정밀 프로파일링 연동 완료
- **DoD-005**: `README.md` 메인 문서 내 Step 2.8 4단계 파이프라인, `--skip-benchmark`, `--fine-grained` 이진 탐색 및 3개 플랫폼 매트릭스 업데이트 완료
- **DoD-006**: `setup.sh` 연동 하위 스크립트들 전면 폴리싱 및 불용/만료 스크립트 정리 완료

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `./setup.sh` 실행 흐름을 4단계 모듈식 파이프라인(Stage 1: 모델 다운로드, Stage 2: GGUF 무결성 실체적 검증 `verify_model_integrity`, Stage 3: 임시 서빙 가동 및 컨텍스트 윈도우 벤치마크, Stage 4: 선정 & 설정 반영)으로 분해 연동해야 한다.
- **FR-002**: System MUST Stage 3 실행 시 임시 인퍼런스 서버를 구동하여 후보 모델 및 컨텍스트 윈도우(2K, 4K, 8K, 16K 등) 확대에 따른 실측 VRAM 소모량과 토큰 생성 속도(TPS)를 정밀 측정해야 한다.
- **FR-003**: System MUST Stage 4 실행 시 벤치마크 결과를 분석하여 VRAM 안전 한계 내 최적 서빙 모델명과 컨텍스트 윈도우 크기(예: 4096, 8192)를 `config/server_config.json`에 원자적 업데이트해야 한다.
- **FR-004**: System MUST `./setup.sh --skip-benchmark` 플래그를 지원하여 Stage 3 벤치마크 단계를 건너뛰고 기존 `server_config.json` 설정값을 보존한 채 15초 이내에 셋업을 완수하도록 해야 한다.
- **FR-005**: System MUST 4단계 모듈식 연동 및 설정 자동 반영을 검증하는 단위 테스트 수트(`tests/unit/test_setup_benchmark_integration.py`)를 작성하고 100% 통과시켜야 한다.
- **FR-006**: System MUST `scripts/benchmark_quality.py` 및 `scripts/benchmark_context_window.py` 내 하드코딩된 상수(베이스라인 수치, 가짜 비율 계산 `* 0.2` 등)와 회피성 목업 로직을 제거하고, VRAM 측정 시 웜업(Warmup) 추론을 우선 수행하여 Lazy Allocation에 의한 과소 측정 레이스 조건을 방지하는 NVML 실측 텔레메트리로 전환해야 한다.
- **FR-007**: System MUST 정밀 프로파일링 모드(`--fine-grained`) 구동 시 1차 2배 스케일링 판정 구간 $[C_{pass}, C_{fail}]$에 대해 512/1024 토큰 블록 얼라인먼트 및 모델 RoPE 최대 지원 한계 캡(`min(physical_max, model_max_rope)`)을 준수하는 이진 탐색(Binary Search)을 실행하고 정밀 결과를 `config/model_context_profiles.json` 및 `data/reports/analysis_report_quality.md`에 원자적 보존해야 한다.
- **FR-008**: System MUST `setup.sh`가 호출하는 연동 하위 스크립트들(`scripts/ensure_models.py`, `scripts/benchmark_context_window.py`, `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh` 등)의 예외 처리, 비대화형 동작 및 100% 경로 분기를 전면 폴리싱 및 모듈화 리팩토링해야 한다.
- **FR-009**: System MUST 용도가 다했거나 만료된 임시/불용 스크립트 및 더미 파일들을 검토하여 안전하게 정리 및 아카이빙해야 한다.

### Key Entities

- **ModularSetupPipeline**: 4단계 모듈식 셋업 파이프라인 엔티티 (`stage_status`, `download_ok`, `integrity_ok`, `recommended_model`, `recommended_context_window`, `benchmark_tps`, `vram_used_mb`).
- **FineGrainedContextProfile**: 정밀 컨텍스트 프로파일 엔티티 (`model_id`, `max_context_length`, `recommended_context_length`, `binary_search_steps`, `peak_vram_mb`, `tpot_tok_per_sec`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./setup.sh` 실행 시 4단계 모듈식 파이프라인 순차 수행 및 최적 서빙 모델/컨텍스트 크기 선정 성공률 100%.
- **SC-002**: `--skip-benchmark` 실행 시 Stage 3 스킵, 기존 설정값 보존 및 15초 이내 고속 셋업 완수율 100% (테스트 수트 내 소요 시간 검증 단정문 포함).
- **SC-003**: 4단계 셋업 모듈 연동 테스트 수트 통과율 100%.
- **SC-004**: `--fine-grained` 정밀 벤치마크 구동 시 하드코딩 값 0% 의존 및 1024 해상도 이진 탐색을 통한 `config/model_context_profiles.json` 저장 성공률 100%.

## Assumptions

- 모델 다운로드(Stage 1)는 `scripts/ensure_models.py`를 통해 연동되며, 무결성 검증(Stage 2) 및 컨텍스트 측정(Stage 3)은 모듈식 파이썬 스크립트(`scripts/benchmark_context_window.py`)로 분해 실행됨.
