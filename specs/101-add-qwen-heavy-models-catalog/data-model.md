# Data Model Specification: 101-add-qwen-heavy-models-catalog

## 1. Entities & Data Schemas

### 1.1 ModelCatalogItem (`config/model_catalog.json`)

`config/model_catalog.json` 내 개별 모델 정의 엔티티 구조:

| Field Name | Type | Required | Description | Example (qwen3.6-27b) |
|------------|------|----------|-------------|-----------------------|
| `name` | string | Yes | 사용자 표기용 모델 이름 | `"Qwen 3.6 27B Instruct"` |
| `repo_id` | string | Yes | HuggingFace Hub 리포지토리 ID | `"unsloth/Qwen3.6-27B-GGUF"` |
| `filename` | string | Yes | HuggingFace GGUF 파일명 | `"Qwen3.6-27B-Instruct-Q4_K_M.gguf"` |
| `clip_filename` | string \| null | No | 시각 CLIP 프로젝터 GGUF 파일명 | `null` |
| `target_dir` | string | Yes | 로컬 저장 상대 경로 | `"models/qwen3.6-27b"` |
| `model_path` | string | Yes | 메인 GGUF 가중치 상대 경로 | `"models/qwen3.6-27b/Qwen3.6-27B-Instruct-Q4_K_M.gguf"` |
| `clip_path` | string \| null | No | CLIP 프로젝터 상대 경로 | `null` |
| `chat_template` | string \| null | No | llama.cpp 대화 템플릿 규격 | `"chatml"` |
| `default_n_ctx` | integer | Yes | 기본 컨텍스트 윈도우 크기 | `4096` |
| `vram_est_mb` | integer | Yes | 베이스 예측 VRAM 점유량 (MB) | `19500` |
| `requires_mmproj` | boolean | Yes | 멀티모달 CLIP 필요 여부 | `false` |
| `quant_type` | string | Yes | 양자화 규격 | `"q4_k_m"` |
| `size_gb` | number | Yes | GGUF 파일 크기 (GB) | `16.5` |
| `task_type` | string | No | 모델 작업 유형 (`llm`, `embedding`, `rerank`) | `"llm"` |

> **VRAM 경계 메모**:
> - `qwen3.6-27b` (`vram_est_mb`: 19,500) & `gemma4-26b-a4b` (`vram_est_mb`: 18,800): 단일 24GB GPU 가용 VRAM(23,576MB) 지원 범위 내 호환.
> - `qwen3.6-35b-a3b` (`vram_est_mb`: 24,500): 단일 24GB GPU 가용 VRAM(23,576MB)을 초과하므로 단일 24GB GPU에서도 Pre-flight 배제되며 Multi-GPU 환경 필요.

---

### 1.2 ModelContextProfile (`config/model_context_profiles.json`)

`scripts/benchmark_context_window.py` 벤치마크 수행 결과 저장 프로파일 엔티티:

```json
{
  "model_key": "qwen3.6-27b",
  "is_supported": false,
  "max_n_ctx": 0,
  "optimal_n_ctx": 0,
  "tps": 0.0,
  "vram_usage_mb": 0,
  "failure_reason": "CUDA OOM Risk: Base VRAM (19500MB) exceeds Usable VRAM (10488MB)",
  "evaluated_at": "2026-08-05T14:50:00Z"
}
```

---

## 2. Complete Model Catalog Key List (14 Models)

```json
[
  "gemma4-e2b",
  "gemma4-e4b",
  "gemma4-12b",
  "gemma4-2b-text",
  "gemma4-4b-text",
  "gemma4-12b-text",
  "gemma4-26b-a4b",
  "qwen3.5-2b",
  "qwen3.5-4b",
  "qwen3.5-9b",
  "qwen3.6-27b",
  "qwen3.6-35b-a3b",
  "bge-m3",
  "bge-reranker-v2-m3"
]
```
