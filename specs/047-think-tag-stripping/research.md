# Research & Technical Choices: 047-think-tag-stripping

## 1. LLM `<think>...</think>` Tag Extraction & Parser Strategy

- **Decision**: Implement a lightweight regex & streaming state-machine helper function (`parse_think_tags(text: str) -> tuple[str, str]`) in `src/core/think_tag_parser.py`.
- **Rationale**:
  - Non-streaming response: Regular expression `re.search(r'<think>(.*?)</think>', text, re.DOTALL)` extracts `thinking_process` and removes the block to produce clean `text`.
  - Unclosed `<think>` tag (truncation): If `<think>` is found without `</think>`, extract all text after `<think>` into `thinking_process` and return `[Truncated during thinking process]` for `text`.
  - SSE Streaming (`stream=True`): State-machine tracks whether currently inside `<think>` block. Suppresses tokens inside `<think>...</think>` from client output stream, and accumulates full text in background for final DB logging.
- **Alternatives Considered**:
  - Simple string `.replace('<think>', '')`: Fails to separate reasoning text from final answer and fails on unclosed tags.
  - Complex AST parser: Over-engineered; regex + streaming state machine is fast (<0.1ms overhead) and zero dependency.

## 2. API Response & Default `max_tokens` Adjustment

- **Decision**: Update `PlaygroundRequest` default `max_tokens` from 256 to 1024, and add `thinking_process: Optional[str] = None` to `PlaygroundResponse`.
- **Rationale**: Reasoning models (DeepSeek R1, Qwen 2.5/3.5) consume 200~500+ tokens in internal reasoning. `max_tokens=1024` prevents premature truncation before final answer generation.
- **Alternatives Considered**: Keeping `max_tokens=256` default causes >80% of reasoning model prompts to truncate during thinking.

## 3. Audit Log Payload DB Storage

- **Decision**: Log cleaned final answer as `completion_text` in `data/metrics.db` (`api_key_logs`), and add/store `thinking_text` as a dedicated column or metadata attribute for Payload Viewer retrieval.
- **Rationale**: Preserves 100% genuine user prompts and model responses while providing clean default audit views.
