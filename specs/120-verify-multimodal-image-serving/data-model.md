# Data Model: 멀티모달(비전) 서빙 검증 데이터 모델

## 1. 엔티티 정의 (Entities)

### MultimodalModelPreset (`src/core/process_manager.py`)

`ProcessManager`가 `config/model_catalog.json`으로부터 읽어들여 런타임 프로세스 제어에 사용하는 내장 뷰 모델입니다.

| Field Name | Type | Required | Description | Example (gemma4-e2b / qwen3.5-9b-vision) |
|---|---|---|---|---|
| `model` | string | Yes | 메인 GGUF 모델 상대 경로 | `"models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf"` |
| `clip` | string | Optional (Yes if `requires_mmproj`) | 비전 프로젝터(mmproj) 상대 경로 | `"models/qwen3.5-9b-vision/mmproj-BF16.gguf"` |
| `chat_template` | string | Yes | 챗 프롬프트 템플릿 | `"chatml"` |
| `vram_est_mb` | integer | Yes | VRAM 점유 추정치 | `9800` |
| `requires_mmproj` | boolean | Yes | 멀티모달 비전 필수 플래그 | `true` |

---

### MultimodalChatMessagePayload (`src/api/routes/inference_api.py`)

OpenAI 규격 `/v1/chat/completions` 요청 내 멀티모달 콘텐츠 메시지 인티티입니다.

| Field Name | Type | Description |
|---|---|---|
| `type` | string | 콘텐츠 종류 (`"text"` 또는 `"image_url"`) |
| `text` | string | 텍스트 프롬프트 (type이 `"text"`일 경우) |
| `image_url` | object | 이미지 URL 또는 Base64 객체 (`{"url": "data:image/jpeg;base64,..."}`) |

---

## 2. 검증 규칙 (Validation Rules)

1. `requires_mmproj == true`인 모델 스폰 시 `clip` 경로가 가리키는 파일이 존재할 경우 `llama-server` 인자에 `--mmproj <clip_path>`가 동적으로 추가된다.
2. `clip` 파일이 존재하지 않는 경우 `ProcessManager` 스폰 단계 또는 파일 점검 스크립트(`ensure_models.py`) 단계에서 파일 미존재(MISSING)로 분류된다.
