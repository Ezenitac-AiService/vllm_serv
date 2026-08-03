# Data Model: Rerank Request & Response Contract Schema

## RerankRequest Entity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Optional | Target reranker model ID (e.g. `bge-reranker-v2-m3`) |
| `query` | string | **Yes** | Search query string |
| `documents` | list[string] | **Yes** | List of candidate text documents |
| `top_n` | integer | Optional | Number of top ranked results to return |

## RerankResponse Entity

| Field | Type | Description |
|-------|------|-------------|
| `object` | string | `list` or `rerank` |
| `results` / `data` | list[dict] | Array of items containing `index` and `relevance_score` |
| `usage` | dict | `prompt_tokens`, `total_tokens` |
