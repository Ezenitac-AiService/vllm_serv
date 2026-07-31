# Research & Technical Choices: 048-think-tag-ui-markdown

## 1. Web Markdown Rendering & Syntax Highlighting Standard (July 2026)

- **Decision**: Integrate `marked.js` (for Markdown parsing) + `DOMPurify` (for XSS sanitization) + `highlight.js` (for code block syntax highlighting) via CDN links in `src/api/static/index.html`.
- **Rationale**:
  - `marked.js` is the industry standard lightweight, high-performance JS Markdown parser.
  - `DOMPurify` guarantees protection against XSS vulnerabilities when rendering raw LLM HTML outputs.
  - `highlight.js` automatically detects code languages (Python, JS, C++, SQL, Bash, JSON) and styles them beautifully with zero build tools required in vanilla JS.
- **Alternatives Considered**:
  - Custom regex Markdown parser: Fails on complex nested lists, tables, and multi-line code blocks.

## 2. Google AI Studio Style Collapsible Sidebar Layout & UX

- **Decision**: Implement a CSS glassmorphism collapsible left sidebar (`#chat-history-sidebar`) in `src/api/static/index.html` and `style.css`.
- **Rationale**:
  - Google AI Studio and ChatGPT interfaces feature a collapsible sidebar containing:
    1. `+ New Chat` button at top.
    2. Vertical scrollable list of active chat sessions.
    3. Active session highlighting.
    4. Session deletion icon (🗑️) on hover.
    5. Collapse toggle button (◀ / ▶) to maximize canvas workspace.

## 3. Persistent SQLite Session Storage (`data/metrics.db`)

- **Decision**: Store chat history in SQLite tables (`playground_sessions` and `playground_messages`) managed by `src/core/metrics_db.py`.
- **Rationale**:
  - Browser `localStorage` can be cleared accidentally and has size limits.
  - SQLite WAL mode backend ensures zero-latency persistence, cross-device sync if hosted, and seamless restoration upon page refresh.
