# Data Model: `config/model_catalog.json` HF 다운로드 URL 원인 분석, 리팩토링 및 404 오류 수렴 검증 (104-fix-catalog-download-urls)

## Core Entities & Models

### 1. ModelCatalogHFUrlSpec
- **Description**: `config/model_catalog.json` 내 카탈로그 모델의 HuggingFace Hub 다운로드 엔드포인트 무결성 및 Instruct/Quantization 설정 엔티티.
- **Fields**:
  - `model_id`: `string` - 모델 고유 식별자 (예: `gemma4-26b-a4b`, `qwen3.6-27b`, `qwen3.6-35b-a3b`)
  - `repo_id`: `string` - HuggingFace Hub 레포지토리 식별자 (예: `unsloth/gemma-4-26B-A4B-it-GGUF`)
  - `filename`: `string` - GGUF 파일명 (예: `gemma-4-26B-A4B-it-UD-Q4_K_M.gguf`, 반드시 `Q4_K_M` 양자화 및 Instruct 버전)
  - `resolved_url`: `string` - `https://huggingface.co/{repo_id}/resolve/main/{filename}`
  - `http_status`: `integer` - HTTP HEAD 요청 응답 코드 (반드시 `200` OK 이어야 함)
  - `requires_mmproj`: `boolean` - 비전 멀티모달 요구 여부 (`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `gemma4-26b-a4b`는 `false` 텍스트 전용)
  - `clip_filename`: `string | null` - 멀티모달 CLIP 파일명 (텍스트 전용 모델은 `null`)

### 2. ModelDownloaderReconciliationSpec
- **Description**: 카탈로그 다운로드 및 메타데이터 정합성 동기화 명세.
- **Fields**:
  - `download_status`: `DownloadStatusEnum` (`NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`)
  - `retry_count`: `integer` - 최대 3회 재시도 카운트
  - `error_type`: `string` - 실패 시 발생 원인 예외 (404 Client Error 등)
