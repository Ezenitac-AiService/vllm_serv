# Feature Specification: Qwen 및 Gemma 4 대형/양자화 모델 카탈로그 확장 및 제외 파이프라인 검증 (101-add-qwen-heavy-models-catalog)

**Feature Branch**: `101-add-qwen-heavy-models-catalog`

**Created**: 2026-08-05

**Status**: Draft (Extended with Gemma 4 26B A4B MoE & Text-Only Variants)

**Input**: User description: "현재 모델 카탈로그에 있는 것과 Qwen3.5-9B-Instruct-4bit 비교하고 Qwen3.6-27B-Instruct-4bit Qwen3.6-35B-A3B-4bit 의 허깅페이스 주소를 리서치해서 카달로그에 추가. gemma4 모델도 양자화 모델을 대대적으로 리서치해서 26B A4B MoE 모델도 카탈로그에 추가 기존 gemma4 모델도 양자화와 텍스트 전용 모델을 리서치해서 '추가'"

## Clarifications & Research Comparison

### Session 2026-08-05

- Q: Qwen 시리즈 버전 및 파라미터 규격(9B는 Qwen3.5, 27B는 Qwen3.6, 35B-A3B MoE는 Qwen3.6)의 HuggingFace GGUF 최신 매핑 정합성은 어떠한가? → A: 9B 모델은 Qwen3.5 계열(unsloth/Qwen3.5-9B-GGUF), 27B 모델은 Qwen3.6 계열(unsloth/Qwen3.6-27B-GGUF), 35B-A3B MoE 모델은 Qwen3.6 계열(unsloth/Qwen3.6-35B-A3B-GGUF)로 최신 Hub 리포지토리 및 Q4_K_M 양자화 규격이 검증 완료되었음을 명세에 확정 기록함.
- Q: Gemma 4 26B A4B MoE 모델 및 기존 Gemma 4 (2B/4B/12B) 텍스트 전용(Text-Only) 양자화 모델의 추가 지정 내역은 어떠한가? → A: Gemma 4 26B A4B MoE (unsloth/gemma-4-26B-A4B-it-GGUF, ~15.8GB, vram_est_mb: 18800MB) 대형 후보 모델과, 기존 Gemma 4 시각(mmproj) 비의존성 텍스트 전용 모델 3종(gemma4-2b-text, gemma4-4b-text, gemma4-12b-text)을 카탈로그 확장 항목으로 추가 수록함.
- Q: 확장 완료 후 카탈로그 내 총 후보 모델 수와 분류 체계는 어떻게 구성되는가? → A: 총 14개 모델 (LLM 인퍼런스/벤치마크 평가 후보 12개 + 보조 임베딩/리랭킹 모델 2개)로 최종 집계 확정함.
- Q: 2026년 8월 기준 HuggingFace 리포지토리 주소, 파일명 및 양자화 규격 검증 결과는 어떠한가? → A: Qwen 3.5(unsloth/Qwen3.5-*), Qwen 3.6(unsloth/Qwen3.6-*), Gemma 4(lmstudio-community 및 unsloth/gemma-4-*), BGE(ggml-org/klnstpr)의 공식 GGUF Q4_K_M / Q8_0 리포지토리 주소 및 파일 구조가 100% 검증되었음을 기록함.
- Q: 다중 GPU VRAM 계층(8G GTX1070/1080/RTX2080, 11G GTX1080Ti, 24G RTX3090, 32G RTX4090/5090, 40G A100, 80G H100) 동적 수용 방식 및 판정 기준은 어떠한가? → A: 스크립트가 NVML 가용 VRAM(Total - 500MB)을 런타임 쿼리하여 8G에서 6개, 11G에서 9개, 24G에서 11개, 32G/40G/80G에서 12개 전체 LLM을 동적으로 자동 판정(`is_supported: true/false`)하도록 수록함.

### Current Catalog vs Qwen 3.5/3.6 & Gemma 4 Series Comparison

- **기존 Qwen 항목 (`qwen3.5-9b`)**:
  - `repo_id`: `unsloth/Qwen3.5-9B-GGUF`, `filename`: `Qwen3.5-9B-Q4_K_M.gguf`, `size_gb`: 5.8 GB, `vram_est_mb`: 9800 MB
- **신규 추가 Qwen 대형 1 (`qwen3.6-27b`)**:
  - `name`: Qwen 3.6 27B Instruct (Q4_K_M)
  - `repo_id`: `unsloth/Qwen3.6-27B-GGUF`, `filename`: `Qwen3.6-27B-Instruct-Q4_K_M.gguf`, `size_gb`: 16.5 GB, `vram_est_mb`: 19500 MB
- **신규 추가 Qwen 대형 2 (`qwen3.6-35b-a3b`)**:
  - `name`: Qwen 3.6 35B A3B Instruct (Q4_K_M MoE)
  - `repo_id`: `unsloth/Qwen3.6-35B-A3B-GGUF`, `filename`: `Qwen3.6-35B-A3B-Q4_K_M.gguf`, `size_gb`: 21.0 GB, `vram_est_mb`: 24500 MB (단일 24GB GPU 가용 VRAM 23,576MB 초과로 Multi-GPU/CPU 오프로드 필요)
- **신규 추가 Gemma 4 대형 3 (`gemma4-26b-a4b`)**:
  - `name`: Gemma 4 26B A4B Instruct (Q4_K_M MoE)
  - `repo_id`: `unsloth/gemma-4-26B-A4B-it-GGUF`, `filename`: `gemma-4-26B-A4B-it-Q4_K_M.gguf`, `size_gb`: 15.8 GB, `vram_est_mb`: 18800 MB
- **신규 추가 Gemma 4 텍스트 전용 3종 (`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`)**:
  - `gemma4-2b-text`: `unsloth/gemma-4-E2B-it-GGUF`, `gemma-4-E2B-it-Q4_K_M.gguf` (1.6GB, vram_est_mb: 2800, requires_mmproj: false)
  - `gemma4-4b-text`: `unsloth/gemma-4-E4B-it-GGUF`, `gemma-4-E4B-it-Q4_K_M.gguf` (2.9GB, vram_est_mb: 5200, requires_mmproj: false)
  - `gemma4-12b-text`: `unsloth/gemma-4-12b-it-GGUF`, `gemma-4-12b-it-Q4_K_M.gguf` (7.2GB, vram_est_mb: 9200, requires_mmproj: false)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Qwen 및 Gemma 4 대형/텍스트 전용 모델 카탈로그 수록 및 확장성 확보 (Priority: P1) 🎯 MVP

시스템 엔지니어가 고성능 GPU 플랫폼(RTX 3090/4090 24GB 이상) 및 다양한 텍스트/모달리티 선택지로의 확장을 대비할 때, `config/model_catalog.json`에 Qwen 3.6 (27B, 35B MoE) 및 Gemma 4 (26B A4B MoE 및 2B/4B/12B 텍스트 전용) 모델들의 HuggingFace 리포지토리 ID, GGUF 파일명, 양자화 규격, 예측 VRAM 용량이 정밀히 등록되어 조회 및 검증 가능해야 합니다.

**Why this priority**: 하드웨어 및 서비스 요구사항 변동 시 카탈로그 변경 없이 서빙 후보군으로 즉시 확장할 수 있도록 종합 메타데이터 구축이 최우선 필요합니다.

**Independent Test**: `config/model_catalog.json` 조회 시 `qwen3.6-27b`, `qwen3.6-35b-a3b`, `gemma4-26b-a4b`, `gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text` 엔티티가 올바른 `repo_id` 및 메타데이터 정보와 함께 로드됨을 확인합니다.

**Acceptance Scenarios**:

1. **Given** 카탈로그 관리 모듈이 가동될 때, **When** `config/model_catalog.json`을 로드하면, **Then** 신규 대형 및 텍스트 전용 모델 메타데이터 엔티티들이 정상 로드되어야 한다.
2. **Given** HuggingFace Hub 다운로더가 호출될 때, **When** `gemma4-26b-a4b` 식별자가 전달되면, **Then** `unsloth/gemma-4-26B-A4B-it-GGUF` 리포지토리 및 `gemma-4-26B-A4B-it-Q4_K_M.gguf` 파일 경로가 올바르게 해석되어야 한다.

---

### User Story 2 - setup.sh 파이프라인에서 VRAM 초과 대형 모델의 정밀 배제 및 오탐 없는 진단 검증 (Priority: P2)

운영자가 11GB VRAM(GTX 1080 Ti 등) 하드웨어 환경에서 `./setup.sh --force-benchmark`를 구동할 때, 카탈로그에 수록된 20GB급 대형 모델들(Qwen 27B/35B, Gemma 4 26B)이 사전 Pre-flight VRAM 용량 점검 또는 실측 이진 탐색 단계에서 안전하게 차단되어 `is_supported: false` 및 구체적 원인이 수록되면서, 파이프라인 크래시 없이 완료되어야 합니다.

**Why this priority**: 지원 불가능한 고용량 모델이 포함되더라도 파이프라인이 중단되지 않고 가용 유효 모델만 서빙 대상으로 자동 선정되는지 검증합니다.

**Independent Test**: `./setup.sh --force-benchmark` 수행 시 대형 모델들이 `is_supported: false`로 프로파일에 수록되고 최종 최적 서빙 모델은 가용 유효 모델로 정상 선정되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 11GB VRAM 자원 환경에서 `--force-benchmark` 구동 시, **When** 대형 모델군을 평가하면, **Then** 프로세스 크래시 없이 `CUDA_OOM_EXCEEDED` 또는 `CUDA OOM Risk` 실패 사유가 기록되며 `is_supported: false`로 배제되어야 한다.
2. **Given** 대형 모델 배제 평가 완납 후, **When** 최적 서빙 모델을 선정할 때, **Then** 가용 유효 모델이 최적 서빙 모델로 결정되어 `config/server_config.json`에 반영되어야 한다.

---

### Edge Cases

- 물리 로컬 디스크에 대형 GGUF 파일이 존재하지 않을 때 `ensure_models.py` / `verify_model_integrity()`가 파일 부재 경고 후 예외 없이 차후 평가로 넘어가는가?
- 가용 VRAM 용량이 대형 모델의 Base VRAM보다 작아 사전 차단될 때 `config/model_context_profiles.json`에 `is_supported: false`가 기록되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `config/model_catalog.json`에 `qwen3.6-27b`, `qwen3.6-35b-a3b`, `gemma4-26b-a4b`, `gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text` 메타데이터 엔티티 등록 완납.
- **DoD-002**: `./setup.sh --force-benchmark` 및 `scripts/benchmark_context_window.py` 수행 시 신규 대형 모델들이 11GB VRAM 환경에서 예외 없이 안전 배제(`is_supported: false`)되고 유효 최적 모델선정이 통과함을 실측 검증.
- **DoD-003**: 프로젝트 전체 단위 테스트 수트 (`uv run pytest tests/unit/`) 100% Pass 및 헌장 원칙 준수.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `config/model_catalog.json`에 `qwen3.6-27b` (HuggingFace: `unsloth/Qwen3.6-27B-GGUF`, 파일: `Qwen3.6-27B-Instruct-Q4_K_M.gguf`) 메타데이터 항목을 추가해야 한다.
- **FR-002**: System MUST `config/model_catalog.json`에 `qwen3.6-35b-a3b` (HuggingFace: `unsloth/Qwen3.6-35B-A3B-GGUF`, 파일: `Qwen3.6-35B-A3B-Q4_K_M.gguf`) 메타데이터 항목을 추가해야 한다.
- **FR-003**: System MUST `config/model_catalog.json`에 `gemma4-26b-a4b` (HuggingFace: `unsloth/gemma-4-26B-A4B-it-GGUF`, 파일: `gemma-4-26B-A4B-it-Q4_K_M.gguf`) 메타데이터 항목을 추가해야 한다.
- **FR-004**: System MUST `config/model_catalog.json`에 Gemma 4 텍스트 전용(Text-Only) 모델 3종(`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `requires_mmproj: false`) 메타데이터 항목을 추가해야 한다.
- **FR-005**: System MUST `scripts/benchmark_context_window.py`에서 `get_candidate_llm_models()`를 수행할 때 신규 추가된 Qwen 및 Gemma 4 모델들이 후보 LLM 평가 목록에 동적으로 포함되도록 보장해야 한다.
- **FR-006**: System MUST 벤치마크 평가 중 가용 VRAM 용량을 초과하는 대형 모델에 대해 사전 Pre-flight VRAM 차단 또는 런타임 OOM 차단을 수행하고, `config/model_context_profiles.json` 프로파일에 `is_supported: false` 및 구체적인 `failure_reason`을 명시 기록해야 한다.
- **FR-007**: System MUST 대형 모델 배제 평가가 완납된 후에도 서빙 가능한 유효 모델 중 가장 높은 TPS를 기록한 최적 모델을 `config/server_config.json`의 서빙 모델로 정상 업데이트해야 한다.

### Key Entities

- **ModelCatalogItem (qwen3.6-27b)**: Qwen 3.6 27B Instruct GGUF 모델 메타데이터 (Q4_K_M 양자화, 16.5GB, vram_est_mb: 19500).
- **ModelCatalogItem (qwen3.6-35b-a3b)**: Qwen 3.6 35B A3B Instruct GGUF MoE 모델 메타데이터 (Q4_K_M 양자화, 21.0GB, vram_est_mb: 24500).
- **ModelCatalogItem (gemma4-26b-a4b)**: Gemma 4 26B A4B Instruct GGUF MoE 모델 메타데이터 (Q4_K_M 양자화, 15.8GB, vram_est_mb: 18800).
- **ModelCatalogItem (gemma4-2b-text, gemma4-4b-text, gemma4-12b-text)**: Gemma 4 텍스트 전용 GGUF 모델 메타데이터 (`requires_mmproj: false`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `config/model_catalog.json`에 Qwen 및 Gemma 4 신규 항목 100% 정상 등록 및 `ModelDownloader` 리포지토리 매핑 성공.
- **SC-002**: `./setup.sh --force-benchmark` 실행 시 대형 모델들이 파이프라인 크래시 없이 `is_supported: false`로 정상 진단 배제됨.
- **SC-003**: 프로젝트 전체 단위 테스트 수트 (`uv run pytest tests/unit/`) 100% Pass.

## Assumptions

- 신규 대형 모델들은 향후 24GB+ VRAM 타깃 GPU 플랫폼 전환 시 서빙 후보군으로 구동된다.
- 11GB VRAM 환경에서는 로컬 가중치 파일 미존재 또는 VRAM 용량 초과로 인하여 지원 불가(`is_supported: false`) 판정을 받는 것이 정상 작동 기준이다.
