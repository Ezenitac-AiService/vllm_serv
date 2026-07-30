# Data Model & Schema Specification: 코드베이스 전체 모델 경로 하드코딩 제거 및 Gemma 4 카탈로그 정합성 보장

**Feature Branch**: `024-fix-seed-pack-gemma4-paths`
**Date**: 2026-07-30
**Spec Reference**: [spec.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/spec.md) | [plan.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/plan.md)

---

## 1. 개요 (Overview)

본 문서는 `config/model_catalog.json`의 단일 진실 소스(SSOT) 데이터 모델 명세, Key Alias 매핑 테이블, 그리고 `ConfigManager` 및 `ModelDownloader`간의 데이터 흐름 및 유효성 검증 규칙을 정의합니다.

---

## 2. Key Entities (핵심 엔티티)

### Entity 1: `ModelCatalogEntry` (단일 모델 메타데이터 스키마)

`config/model_catalog.json` 내 최상위 키(`model_id`)에 매핑되는 구조화된 메타데이터 엔티티입니다.

```json
{
  "name": "Gemma 4 E2B",
  "repo_id": "lmstudio-community/gemma-4-E2B-it-GGUF",
  "filename": "gemma-4-E2B_q4_0-it.gguf",
  "clip_filename": "gemma-4-E2B-it-mmproj.gguf",
  "target_dir": "models/gemma4-e2b",
  "model_path": "models/gemma4-e2b/gemma-4-E2B_q4_0-it.gguf",
  "clip_path": "models/gemma4-e2b/gemma-4-E2B-it-mmproj.gguf",
  "chat_template": "gemma",
  "default_n_ctx": 4096,
  "vram_est_mb": 3500,
  "requires_mmproj": true,
  "quant_type": "q4_0",
  "size_gb": 1.8
}
```

#### 필드 상세 명세 및 검증 규칙

| 필드명 | 타입 | 필수 여부 | 설명 및 유효성 검증 규칙 |
|---|---|---|---|
| `name` | `str` | 필수 | 모델 표기용 디스플레이 이름 |
| `repo_id` | `str` | 필수 | Hugging Face Hub 레포지토리 ID (예: `lmstudio-community/gemma-4-E2B-it-GGUF`) |
| `filename` | `str` | 필수 | 주 GGUF 모델 파일 이름 |
| `clip_filename` | `Optional[str]` | 선택 | Multimodal CLIP projector GGUF 파일 이름 (`requires_mmproj=true` 시 필수) |
| `target_dir` | `str` | 필수 | 로컬 저장 대상 상대 경로 (예: `models/gemma4-e2b`) |
| `model_path` | `str` | 필수 | 모델 파일의 상대 경로 (`target_dir/filename`과 일치) |
| `clip_path` | `Optional[str]` | 선택 | CLIP projector 파일의 상대 경로 (`requires_mmproj=true` 시 필수) |
| `chat_template` | `str` | 필수 | llama.cpp 프롬프트 템플릿 종류 (`gemma`, `chatml` 등) |
| `default_n_ctx` | `int` | 필수 | 기본 컨텍스트 길이 (`>= 2048`) |
| `vram_est_mb` | `int` | 필수 | 추론 시 추정 VRAM 사용량 (MB) |
| `requires_mmproj` | `bool` | 필수 | 멀티모달 mmproj 파일 동시 다운로드 및 로드 필요 여부 |
| `quant_type` | `str` | 필수 | 양자화 규격 (`q4_0`, `qat_q4_0`, `q4_k_m`) |
| `size_gb` | `float` | 필수 | 디스크 소요 용량 (GB) |

---

## 3. Gemma 4 모델 카탈로그 정합성 정의

`config/model_catalog.json` 내 Gemma 4 카탈로그 3종 정밀 픽스 스판 명세:

| Catalog Key | `repo_id` | `filename` | `clip_filename` | `target_dir` |
|---|---|---|---|---|
| **`gemma4-e2b`** | `lmstudio-community/gemma-4-E2B-it-GGUF` | `gemma-4-E2B_q4_0-it.gguf` | `gemma-4-E2B-it-mmproj.gguf` | `models/gemma4-e2b` |
| **`gemma4-e4b`** | `lmstudio-community/gemma-4-E4B-it-GGUF` | `gemma-4-E4B_q4_0-it.gguf` | `gemma-4-E4B-it-mmproj.gguf` | `models/gemma4-e4b` |
| **`gemma4-12b`** | `lmstudio-community/gemma-4-12b-it-GGUF` | `gemma-4-12b-it-qat-q4_0.gguf` | `mmproj-gemma-4-12b-it-qat-q4_0.gguf` | `models/gemma4-12b` |

---

## 4. Key Alias 매핑 규격 (Legacy Compatibility)

기존 레거시 스크립트와의 호환성을 유지하기 위한 `ConfigManager` 내부 키 변환 맵:

```python
MODEL_KEY_ALIASES = {
    "gemma4-2b": "gemma4-e2b",
    "gemma4-4b": "gemma4-e4b",
    "gemma-4-2b": "gemma4-e2b",
    "gemma-4-4b": "gemma4-e4b",
    "gemma-4-12b": "gemma4-12b",
}
```

`ConfigManager.get_model_config(model_id)` 호출 시 입력된 `model_id`가 에일리어스에 존재하면 공식 표준 `model_id`로 자동 변환하여 정합성을 보장합니다.
