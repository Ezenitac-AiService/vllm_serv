# Data Model & DB Schema: 048-think-tag-ui-markdown

## 1. Database Schema (`data/metrics.db`)

### Table: `playground_sessions`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Session UUID or timestamp ID (e.g. `sess_1722350000`) |
| `title` | TEXT | NOT NULL | Session title (auto-generated from 1st prompt) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last activity timestamp |

### Table: `playground_messages`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique message ID |
| `session_id` | TEXT | FOREIGN KEY -> `playground_sessions(id)` | Session reference |
| `role` | TEXT | NOT NULL | `user` or `assistant` |
| `content` | TEXT | NOT NULL | Message text / clean answer |
| `thinking_process` | TEXT | NULLABLE | Extracted reasoning trace string |
| `timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Message timestamp |

---

## 2. UI State Entities (`src/api/static/app.js`)

### `ThinkDisplayMode` Enum

- `'show'`: Always expand `<think>` blocks in chat thread.
- `'collapse'`: Show `<think>` block during streaming, auto-collapse on completion. (Default)
- `'off'`: Hide `<think>` block completely.
