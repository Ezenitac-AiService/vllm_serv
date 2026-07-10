# Phase 1: Data Model & Entities

### `PresetConfiguration`
- `id`: string (e.g., "preset-rag")
- `name`: string (UI 표시 이름, 예: "대용량 문서 요약 및 RAG")
- `model_id`: string ("gemma4-4b")
- `n_ctx`: int (34000)
- `description`: string (프리셋 설명)

### `ServerStatus`
- `state`: enum ("LOADING", "READY", "UNLOADED", "ERROR")
- `current_model`: string | null (현재 로드된 모델 ID)
- `current_n_ctx`: int | null (현재 로드된 컨텍스트 길이)
- `vram_total`: int (하드웨어 총 VRAM - MB)
- `vram_used`: int (사용 중인 VRAM - MB)
- `hardware_limits`: object (각 모델별 OOM을 피할 수 있는 최대 안전 n_ctx 값 매핑)
  - 예: `{"gemma4-12b": 9500, "gemma4-4b": 35000}`
