# Interface Contract: Playground Chat Sessions API

## 1. `GET /dashboard/api/playground/sessions`
- **Response**: List of session summaries.
  ```json
  [
    {
      "id": "sess_1722350000",
      "title": "Explain Black Holes",
      "created_at": "2026-07-30 16:00:00",
      "updated_at": "2026-07-30 16:05:00"
    }
  ]
  ```

## 2. `GET /dashboard/api/playground/sessions/{session_id}/messages`
- **Response**: Full message history for specified session.
  ```json
  [
    {
      "id": 1,
      "role": "user",
      "content": "Explain Black Holes",
      "thinking_process": null,
      "timestamp": "2026-07-30 16:00:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "A black hole is...",
      "thinking_process": "Searching physics knowledge...",
      "timestamp": "2026-07-30 16:00:02"
    }
  ]
  ```

## 3. `DELETE /dashboard/api/playground/sessions/{session_id}`
- **Response**: `{"status": "success", "deleted_session_id": "sess_1722350000"}`
