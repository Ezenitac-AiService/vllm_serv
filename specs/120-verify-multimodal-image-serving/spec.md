# Feature Specification: 멀티모달(비전) 모델 로딩 및 이미지 입력 서빙 검증 (verify-multimodal-image-serving)

**Feature Branch**: `120-verify-multimodal-image-serving`

**Created**: 2026-08-08

**Status**: Draft (Remediated for 32GB RAM / 11GB VRAM Hardware Tier)

**Input**: User description: "우리 gemma4 모델들은 멀티모달이야, 이거 제대로 모델 로드하고 서비스해? qwen3.5 9b 비전 모델도 카탈로그에 추가했는데, 이거 제대로 이미지 입력 받는 준비가 되어있는거 맞는기 검토, 검증, 분석해봐. 서버 사양: 32GB RAM / 11GB VRAM"

## Clarifications

### Session 2026-08-08

- Q: 2026년 최신 VLM/멀티모달 최신 레퍼런스 기준 이미지 입력 페이로드 규격 및 처리 방식을 어떻게 확정할 것인가? → A: OpenAI 표준 `image_url` 규격을 채택하여 Data URL Base64 (`data:image/jpeg;base64,...`) 및 원격 HTTP(S) URL 방식을 모두 지원하고, 백엔드 `llama-server` 인퍼런스 엔진에 `--mmproj` 비전 투영기를 결합하여 시각적 컨텍스트를 안정적으로 역방향 프록시 처리한다.
- Q: 32GB RAM / 11GB VRAM 서버 환경에서 대용량 Base64 페이로드 공격 및 VRAM OOM 방어를 어떻게 보장할 것인가? → A: 역방향 프록시 레이어에서 최대 HTTP 요청 바이트 크기를 25MB로 제한하고, 11GB VRAM 한계 내에서 멀티모달 모델 스폰 시 VRAM 점유 추정치를 사전에 검증한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gemma 4 및 Qwen 3.5 9B Vision 멀티모달 모델 바인딩 및 구동 검증 (Priority: P1)

사용자는 32GB RAM / 11GB VRAM 서버 환경에 등록된 멀티모달 모델(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-9b-vision`)을 서빙 모델로 선택했을 때, C++ 백엔드 인퍼런스 엔진(`llama-server`)이 비전 프로젝터(`--mmproj`) 파일과 함께 11GB VRAM 범위 내에서 안정적으로 구동되는지 검증하기를 원합니다.

**Why this priority**: 비전 프로젝터(`mmproj`) 파일 결합 및 11GB VRAM 점유량 사전 검증이 이뤄지지 않으면 GPU OOM 또는 프로세스 크래시가 발생하므로 구동 및 바인딩 검증이 최우선입니다.

**Independent Test**: `ProcessManager`를 통해 멀티모달 모델을 스폰할 때 생성되는 명령행 인자에 `--mmproj` 옵션 및 해당 프로젝터 경로(`clip_path`)가 추가되는지 및 11GB VRAM 한계가 검증되는지 실측 단정합니다.

**Acceptance Scenarios**:

1. **Given** `gemma4-e2b` 또는 `qwen3.5-9b-vision` 모델이 선택된 상태에서, **When** 백엔드 프로세스 스폰을 수행하면, **Then** `llama-server` 인자 목록에 `--mmproj <clip_path>` 플래그가 반드시 포함되어 구동되어야 한다.
2. **Given** 카탈로그 상의 `requires_mmproj: true` 모델에 대해, **When** 비전 프로젝터 파일이 존재하지 않거나 11GB VRAM 용량을 초과하는 경우, **Then** 시스템은 구동을 차단하고 명확한 예외 메시지를 반환해야 한다.

---

### User Story 2 - OpenAI 호환 이미지 입력 Payload (`image_url` / Base64) 및 25MB 크기 제한 라우팅 검증 (Priority: P2)

사용자는 클라이언트가 OpenAI API 규격에 맞춰 이미지 데이터(`image_url` 내 HTTP URL 또는 base64 데이터)를 포함하여 요청을 보낼 때, 25MB 크기 제한 내에서 프록시가 이를 안전하게 전달하기를 원합니다.

**Why this priority**: 메모리가 한정된 32GB RAM / 11GB VRAM 서버에서 과도한 크기의 Base64 데이터 전송 시 발생할 수 있는 메모리 고갈(OOM)을 원천 방지해야 합니다.

**Independent Test**: 25MB 이하의 정상 이미지 페이로드는 200 OK 응답을 반환하고, 25MB 초과 페이로드는 HTTP 413 (Payload Too Large) 에러를 즉시 반환하는지 단정합니다.

**Acceptance Scenarios**:

1. **Given** 25MB 이하의 텍스트와 `image_url` 데이터가 결합된 요청 메시지가 전송될 때, **When** 역방향 프록시를 통과하면, **Then** 페이로드가 누락/훼손 없이 백엔드 엔진으로 전송되어 200 OK 응답을 반환해야 한다.
2. **Given** 25MB를 초과하는 대용량 Base64 이미지 요청 메시지가 전송될 때, **When** 프록시 수신 단계에서, **Then** 백엔드로 전달되지 않고 HTTP 413 Payload Too Large 에러가 반환되어야 한다.

---

### Edge Cases

- 25MB 초과 페이로드 수신 시 서버 RAM/VRAM 메모리 버퍼 폭증 방지 및 HTTP 413 반환 여부.
- 11GB VRAM 하드웨어 타겟에서 `gemma4-12b` 구동 시 VRAM 점유 한계 포착 여부.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: Gemma 4 3종 및 Qwen 3.5 9B Vision 모델의 `--mmproj` 비전 프로젝터 로딩 검증 수트가 작성되고 통과한다.
- **DoD-002**: 25MB 이하 이미지 페이로드 전달 및 25MB 초과 페이로드 413 에러 방어가 검증된다.
- **DoD-003**: 멀티모달 서빙 검증 단위/통합 테스트 코드(`uv run pytest`)가 100% 통과한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 멀티모달 모델(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-9b-vision`) 스폰 시 `ProcessManager`를 통해 `--mmproj <clip_path>` 옵션을 `llama-server` 명령행에 정확히 바인딩해야 한다.
- **FR-002**: 시스템은 `ModelDownloader` 및 `ensure_models.py` 실행 시 멀티모달 모델의 메인 가중치 파일과 `clip_filename` 비전 프로젝터 파일의 존재 여부를 모두 검증해야 한다.
- **FR-003**: 시스템 역방향 프록시(`inference_api.py`)는 OpenAI 표준 규격의 이미지 요청 페이로드(`type: "image_url"`)를 훼손 없이 멀티모달 백엔드로 전달해야 한다.
- **FR-004**: 시스템은 비전 프로젝터 미존재 또는 로드 실패 시 유용한 오류 메시지와 함께 상태 코드 503 또는 400 에러를 리포팅해야 한다.
- **FR-005**: 시스템 역방향 프록시는 32GB RAM / 11GB VRAM 서버 방어를 위해 HTTP 요청 페이로드 최대 크기를 25MB로 제한하고 초과 시 HTTP 413 에러를 반환해야 한다.
- **FR-006**: 시스템은 11GB VRAM 타겟 환경에서 멀티모달 모델 스폰 시 사전 VRAM 점유 추정치를 검증해야 한다.

### Key Entities *(include if feature involves data)*

- **Multimodal Model Specifications (`config/model_catalog.json`)**:
  - `gemma4-e2b`: `requires_mmproj: true`, `clip_filename: "mmproj-gemma-4-E2B-it-BF16.gguf"`
  - `gemma4-e4b`: `requires_mmproj: true`, `clip_filename: "mmproj-gemma-4-E4B-it-BF16.gguf"`
  - `gemma4-12b`: `requires_mmproj: true`, `clip_filename: "mmproj-gemma-4-12B-it-BF16.gguf"`
  - `qwen3.5-9b-vision`: `requires_mmproj: true`, `clip_filename: "mmproj-BF16.gguf"`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 멀티모달 모델 4종의 `--mmproj` 인자 바인딩 및 파일 검증 테스트 100% 통과.
- **SC-002**: 25MB 제한을 포함한 이미지 입력 페이로드 프록시 라우팅 테스트 100% 통과.
- **SC-003**: `uv run pytest` 회귀 검증 수트가 오류 없이 100% 통과.

## Assumptions

- 서버 사양은 32GB System RAM 및 11GB GPU VRAM 환경을 기반으로 동작한다.
- OpenAI 표준 이미지 요청 형식인 `image_url` 객체 형태의 페이로드(Base64 및 HTTP URL)를 표준 지원 대상으로 설정한다.
