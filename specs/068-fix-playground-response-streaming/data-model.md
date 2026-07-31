# Data Model: AI Playground SSE 스트리밍 응답 렌더링 및 Qwen/DeepSeek 사고 과정 파싱 보장 (068-fix-playground-response-streaming)

**Feature**: `068-fix-playground-response-streaming`

## Playground Streaming Event Protocol Schemes

### 1. SSE Stream Data Chunk Parsing Scheme
- **`reasoning_piece`**: `delta.get("reasoning_content") or delta.get("reasoning")`
- **`content_piece`**: `delta.get("content") or choice.get("text")`
- **Events**:
  - `event: think_start` / `data: {}`
  - `data: {"think": "<thinking_tokens>"}`
  - `event: think_end` / `data: {}`
  - `data: {"text": "<answer_tokens>"}`
  - `event: metrics` / `data: {"ttft_ms": ..., "token_speed_tok_s": ...}`
  - `data: [DONE]`

### 2. MetricsDB Safe Initialization Scheme
- **`get_metrics_db()`**: Returns singleton `MetricsDB` instance, instantiated lazily on first access.
- **`metrics_db`**: `_LazyMetricsDBProxy` wrapper avoiding top-level module import disk access.
