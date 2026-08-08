# Data Model: Qwen 3.5 9B 멀티모달 모델 카탈로그 스키마

## 1. 엔티티 정의 (Entities)

### ModelCatalogEntry (`config/model_catalog.json`)

`vllm_serv` 시스템에서 서비스 가능한 LLM/VLM 모델의 사양 및 파일 경로 정보를 보관하는 데이터 구조입니다.

| Field Name | Type | Required | Description | Example (qwen3.5-9b-vision) |
|---|---|---|---|---|
| `name` | string | Yes | 사용자 표시용 모델 명칭 | `"Qwen 3.5 9B Vision"` |
| `repo_id` | string | Yes | Hugging Face 저장소 ID | `"unsloth/Qwen3.5-9B-GGUF"` |
| `filename` | string | Yes | 메인 GGUF 가중치 파일명 | `"Qwen3.5-9B-Q4_K_M.gguf"` |
| `clip_filename` | string | No (Yes if `requires_mmproj`) | 비전 프로젝터(mmproj) 파일명 | `"mmproj-BF16.gguf"` |
| `target_dir` | string | Yes | 모델 파일 저장 타겟 로컬 디렉터리 | `"models/qwen3.5-9b-vision"` |
| `model_path` | string | Yes | 메인 GGUF 가중치 상대 경로 | `"models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf"` |
| `clip_path` | string | No (Yes if `requires_mmproj`) | 비전 프로젝터 상대 경로 | `"models/qwen3.5-9b-vision/mmproj-BF16.gguf"` |
| `chat_template` | string | Yes | 챗 템플릿 종류 | `"chatml"` |
| `default_n_ctx` | integer | Yes | 기본 컨텍스트 윈도우 크기 | `4096` |
| `vram_est_mb` | integer | Yes | 추정 VRAM 사용량 (MB) | `9800` |
| `requires_mmproj` | boolean | Yes | 멀티모달(mmproj) 필수 여부 | `true` |
| `quant_type` | string | Yes | 양산 정밀도 | `"q4_k_m"` |
| `size_gb` | float | Yes | 모델 용량 (GB) | `5.8` |
| `n_layers` | integer | Optional | 레이어 수 | `40` |
| `n_heads` | integer | Optional | 헤드 수 | `32` |
| `n_head_kv` | integer | Optional | KV 헤드 수 | `8` |
| `head_dim` | integer | Optional | 헤드 임베딩 차원 | `128` |
| `max_n_ctx` | integer | Optional | 최대 컨텍스트 윈도우 | `131072` |

---

## 2. 검증 규칙 (Validation Rules)

1. **상호작용 검증**: `requires_mmproj`가 `true`일 경우, `clip_filename`과 `clip_path`는 절대 `null`이어서는 안 되며 유효한 문자열 경로여야 한다.
2. **하위 호환성 검증**: 기존 `qwen3.5-9b` 엔티티의 `requires_mmproj`는 `false`로 유지되며, `clip_filename` 및 `clip_path`는 `null` 상태를 유지한다.
3. **디렉터리 무결성**: `model_path`와 `clip_path`는 `target_dir` 하위에 위치해야 한다.
