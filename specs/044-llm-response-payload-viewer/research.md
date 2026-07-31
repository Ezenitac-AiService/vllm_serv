# Research & Technical Choices: 044-llm-response-payload-viewer

## 1. Google AI Studio 2026 Style UI/UX Architecture
- **Decision**: 2-Column Chat Thread layout (`index.html` & `app.js`) with responsive side parameter panel.
- **Rationale**: Direct alignment with industry standards for LLM developer playgrounds (Google AI Studio 2026, OpenAI Playground 3.0).
- **Alternatives Considered**: Single static textarea (legacy) - discarded as poor UX for multi-turn inference.

## 2. Server-Sent Events (SSE) Token Streaming
- **Decision**: Fetch with `ReadableStream` decoding `/v1/chat/completions` (stream=true) in FastAPI & Vanilla JS.
- **Rationale**: Smooth typewriter token animation experience without blocking UI thread.

## 3. SQLite Payload Storage Schema
- **Decision**: `ALTER TABLE api_key_logs ADD COLUMN prompt_text TEXT; ALTER TABLE api_key_logs ADD COLUMN completion_text TEXT;` in `src/core/metrics_db.py`.
- **Rationale**: Minimal migration overhead, native WAL mode support, sub-millisecond payload retrieval by `request_id`.
