# Quickstart & Validation Guide: 047-think-tag-stripping

## Validation Commands & Verification Results

### 1. Run Unit Test Suite for Think-Tag Stripping
```bash
uv run pytest tests/unit/test_think_tag_stripping.py -v
```
**Result**: `5 passed in 0.50s` (100% Pass)

### 2. Run Full Regression Suite
```bash
uv run pytest tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py -v
```
**Result**: `9 passed in 0.56s` (100% Pass)

---

## Verification Scenarios Tested

1. **Standard Response with `<think>` tag**:
   - Input: `<think>\nStep 1: Calculate 2+2.\nStep 2: Result is 4.\n</think>\n\nAnswer: 4`
   - Parsed `text`: `Answer: 4`
   - Parsed `thinking_process`: `Step 1: Calculate 2+2.\nStep 2: Result is 4.`

2. **Unclosed `<think>` tag (Truncation)**:
   - Input: `<think>\nReasoning started but tokens ran out...`
   - Parsed `text`: `[Truncated during thinking process]`
   - Parsed `thinking_process`: `Reasoning started but tokens ran out...`

3. **Disabled Tag Stripping (`strip_think_tags=False`)**:
   - Output contains raw `<think>` tag block in `text`.

4. **SSE Real-time Streaming Filter (`ThinkTagStreamFilter`)**:
   - Stream output tokens suppress `<think>...</think>` content in real-time while accumulating thinking process for DB audit logs.

5. **Payload Viewer Integration**:
   - `GET /dashboard/api/audit/payload/{id}` returns `thinking_text` payload field for audit accordion UI.
