# Data Model: 2026 최신 기준 리팩토링 분석 명세 (027-architecture-refactoring-analysis)

## Data Entities

### 1. SpeculativeDecodingConfig

Speculative Decoding 적용을 위한 메인 모델-드래프트 모델 페어링 엔티티.

| Field Name | Type | Description | Constraints / Examples |
|---|---|---|---|
| `target_model_id` | `str` | 메인 타겟 모델 ID | `"qwen3.5-4b"`, `"gemma4-12b"` |
| `draft_model_id` | `str` | 초경량 드래프트 모델 ID | `"qwen3.5-2b"`, `"gemma4-e2b"` |
| `is_enabled` | `bool` | Speculative Decoding 활성화 여부 | `True` |
| `vram_overhead_mb` | `int` | 드래프트 모델 예상 VRAM 점유량 | `1500` (1.5GB 이내) |

### 2. StructuredOutputSpec

OpenAI `response_format` 파라미터 및 문법 제약 규격 엔티티.

| Field Name | Type | Description | Constraints / Examples |
|---|---|---|---|
| `format_type` | `str` | 응답 포맷 형식 | `"json_object"`, `"json_schema"` |
| `json_schema` | `Optional[Dict[str, Any]]` | JSON Schema 명세 | `{"type": "object", "properties": {...}}` |
| `gbnf_grammar` | `Optional[str]` | 변환된 GBNF 문법 스트링 | `"root ::= object ..."` |
