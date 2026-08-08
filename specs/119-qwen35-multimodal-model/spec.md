# Feature Specification: Qwen 3.5 9B 멀티모달 모델 검증 및 별도 카탈로그 등록 (qwen35-multimodal-model)

**Feature Branch**: `119-qwen35-multimodal-model`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "허깅 페이스 모델을 검색해서, qwen3.5 9b 모델이 멀티모달인지 확인하고, 현재 카탈로그에 있는 모델이 멀티모달이 아니면 찾아서 추가하기"

## Clarifications

### Session 2026-08-08

- Q: 기존 `qwen3.5-9b` 카탈로그 항목을 직접 수정할 것인가, 신규 별도 카탈로그 항목으로 추가할 것인가? → A: 기존 `qwen3.5-9b` 항목은 텍스트 전용으로 그대로 유지하여 운영 중인 서비스 영향도를 최소화하고, 비전/멀티모달 모델은 신규 카탈로그 엔트리로 별도 추가한다.
- Q: 신규 멀티모달 모델의 카탈로그 키 식별자(ID) 명칭은 무엇으로 설정할 것인가? → A: Option A (`qwen3.5-9b-vision`) - 기존 `qwen3.5-9b` 텍스트 모델과 수평적으로 구별되는 `qwen3.5-9b-vision` 식별자를 사용한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Qwen 3.5 9B 멀티모달 여부 검증 및 별도 카탈로그 항목(`qwen3.5-9b-vision`) 추가 (Priority: P1)

사용자는 허깅페이스(Hugging Face) 상의 Qwen 3.5 9B 모델이 이미지/비전 처리 능력을 갖춘 멀티모달 모델인지 확인하고, 기존 `qwen3.5-9b` 텍스트 전용 항목에 영향을 주지 않도록 vllm_serv 시스템의 모델 카탈로그(`config/model_catalog.json`)에 멀티모달 지원 비전 모델 식별자인 `qwen3.5-9b-vision`을 별도로 신규 등록하기를 원합니다.

**Why this priority**: 현재 운영 중인 `qwen3.5-9b` 서비스를 무중단 유지하면서, 신규 비전/멀티모달 서비스에 필요한 `requires_mmproj: true` 및 `clip_filename` (mmproj) 연동 모델 항목을 안전하게 확장할 수 있습니다.

**Independent Test**: 카탈로그 파일(`config/model_catalog.json`)을 조회하여 기존 `qwen3.5-9b` 항목이 텍스트 전용(`requires_mmproj: false`)으로 유지되고, 신규 비전 모델 항목인 `qwen3.5-9b-vision`에 멀티모달 관련 설정(`clip_filename: "mmproj-BF16.gguf"`, `clip_path: "models/qwen3.5-9b-vision/mmproj-BF16.gguf"`, `requires_mmproj: true`)이 올바르게 추가되었는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 허깅페이스 `unsloth/Qwen3.5-9B-GGUF` 모델에 `mmproj-BF16.gguf` 비전 프로젝터가 존재함이 검증된 상태에서, **When** 카탈로그 업데이트를 수행하면, **Then** 기존 `qwen3.5-9b` 항목은 변경되지 않고 신규 비전 모델 엔트리 `qwen3.5-9b-vision`이 `requires_mmproj: true` 및 `clip_filename`, `clip_path` 설정과 함께 추가되어야 한다.
2. **Given** 신규 추가된 비전 모델 카탈로그 항목(`qwen3.5-9b-vision`)을 바탕으로, **When** 모델 검증 스크립트(`scripts/ensure_models.py` 등)나 자동 다운로더를 실행하면, **Then** 메인 `.gguf` 파일과 `mmproj` 파일이 감지 및 다운로드 타겟으로 파싱되어야 한다.

---

### User Story 2 - 신규 멀티모달 모델(`qwen3.5-9b-vision`) 구동 및 서버 설정 연동 (Priority: P2)

사용자는 신규 추가된 `qwen3.5-9b-vision` 멀티모달 카탈로그 엔트리를 vllm_serv 서비스의 실행 모델로 선택했을 때, C++ 백엔드 인퍼런스 엔진(`llama-server`)이 비전 프로젝터(`--mmproj`) 옵션과 함께 정상 구동되는 것을 원합니다.

**Why this priority**: 새로 추가된 멀티모달 카탈로그 엔트리가 실제 백엔드 인퍼런스 실행 파이프라인과 완벽히 연동되어 비전/이미지 입력 처리 서비스를 제공할 수 있어야 합니다.

**Independent Test**: `config/server_config.json` 또는 환경변수로 신규 멀티모달 모델(`qwen3.5-9b-vision`)을 지정하고 구동 스크립트(`scripts/start_server.sh`)를 실행할 때 생성되는 명령 파라미터에 `--mmproj` 플래그 및 해당 프로젝터 경로가 바인딩되는지 테스트합니다.

**Acceptance Scenarios**:

1. **Given** `qwen3.5-9b-vision` 멀티모달 모델이 선택된 상태에서, **When** 서버 구동 스크립트를 호출하면, **Then** `llama-server` 인스턴스가 `--mmproj` 옵션에 비전 프로젝터 경로를 전달받아 정상 실행된다.

---

### Edge Cases

- 허깅페이스 저장소에 비전 프로젝터 파일(`mmproj-BF16.gguf` 등)이 여러 정밀도(BF16, F16, F32)로 존재할 때 어떤 파일명을 기본값으로 선택할 것인가? (기본값: 기존 gemma4 등 프로젝트 컨벤션에 맞춰 `mmproj-BF16.gguf` 사용)
- 기존 `qwen3.5-9b` 모델 디렉터리와 신규 `qwen3.5-9b-vision` 모델 디렉터리의 분리 저장 구조(`models/qwen3.5-9b-vision/`)가 다운로드 및 서버 구동 시 충돌 없이 작동하는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 허깅페이스 조사 결과를 바탕으로 Qwen 3.5 9B의 멀티모달(Vision) 지원 여부 및 `mmproj` 파일 사양이 밝혀지고 명세에 문서화된다.
- **DoD-002**: 기존 `qwen3.5-9b` 텍스트 전용 항목을 보존하고, `config/model_catalog.json`에 `qwen3.5-9b-vision` 멀티모달 지원 엔트리가 올바르게 추가된다.
- **DoD-003**: 모델 카탈로그 무결성 검증 및 모델 다운로드/구동 연동 테스트 코드(`uv run pytest`)가 100% 통과한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 허깅페이스 `unsloth/Qwen3.5-9B-GGUF` (또는 관련 공식/검증된 GGUF 리포지토리)의 비전 프로젝터(`mmproj-BF16.gguf`) 파일 정보를 검증해야 한다.
- **FR-002**: 시스템은 기존 `qwen3.5-9b` 카탈로그 항목(텍스트 전용, `requires_mmproj: false`)을 그대로 보존해야 한다.
- **FR-003**: 시스템은 `config/model_catalog.json`에 신규 카탈로그 엔트리 `qwen3.5-9b-vision`을 추가하고 `requires_mmproj: true`, `clip_filename: "mmproj-BF16.gguf"`, `clip_path: "models/qwen3.5-9b-vision/mmproj-BF16.gguf"`, `model_path: "models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf"`로 설정해야 한다.
- **FR-004**: 시스템 모델 동기화/다운로드 스크립트(`scripts/ensure_models.py`)는 `qwen3.5-9b-vision` 비전 모델 처리 시 메인 GGUF 파일과 `mmproj` 파일이 모두 갖춰져 있는지 검증해야 한다.
- **FR-005**: 시스템 서버 구동 스크립트(`scripts/start_server.sh`)는 `qwen3.5-9b-vision` 비전 모델 실행 시 `llama-server`에 `--mmproj` 옵션을 전달하여 멀티모달 인퍼런스를 지원해야 한다.

### Key Entities *(include if feature involves data)*

- **Model Catalog Entry (`config/model_catalog.json`)**:
  - Existing Entry: `qwen3.5-9b` (Text-Only, `requires_mmproj: false`)
  - New Entry: `qwen3.5-9b-vision` (Vision/Multimodal)
    - `name`: "Qwen 3.5 9B Vision"
    - `repo_id`: "unsloth/Qwen3.5-9B-GGUF"
    - `filename`: "Qwen3.5-9B-Q4_K_M.gguf"
    - `clip_filename`: "mmproj-BF16.gguf"
    - `target_dir`: "models/qwen3.5-9b-vision"
    - `model_path`: "models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf"
    - `clip_path`: "models/qwen3.5-9b-vision/mmproj-BF16.gguf"
    - `chat_template`: "chatml"
    - `default_n_ctx`: 4096
    - `vram_est_mb`: 9800
    - `requires_mmproj`: true
    - `quant_type`: "q4_k_m"

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 기존 `qwen3.5-9b` 카탈로그 항목의 동작 및 하위 호환성이 100% 유지되고, 신규 `qwen3.5-9b-vision` 비전 모델 엔트리가 `requires_mmproj: true`로 카탈로그 검증을 통과한다.
- **SC-002**: `uv run pytest` 실행 시 모델 카탈로그 무결성 검증 및 구성 요소 테스트 수트가 오류 없이 100% 통과한다.
- **SC-003**: 모델 파일 확인 스크립트(`ensure_models.py`) 실행 시 `qwen3.5-9b-vision` 모델의 메인 파일과 mmproj 비전 프로젝터가 모두 정확하게 식별/검증된다.

## Assumptions

- 허깅페이스의 `unsloth/Qwen3.5-9B-GGUF` 리포지토리에 제공되는 `mmproj-BF16.gguf`는 llama.cpp 백엔드의 `--mmproj` 파라미터와 호환된다.
- 기존 운영 서비스 호환성을 위해 `qwen3.5-9b` 항목은 변경하지 않고, 신규 비전 모델 카탈로그 항목(`qwen3.5-9b-vision`)을 추가한다.
