# Data Model & Sequence Diagram: `079-fix-reranker-404-routing`

**Feature Directory**: [`specs/079-fix-reranker-404-routing`](file:///home/dev/storage/vllm_serv/specs/079-fix-reranker-404-routing)  
**Spec**: [`spec.md`](spec.md) | **Research**: [`research.md`](research.md)  

---

## 1. Sequence Diagram: Reranker Reverse Proxy Path Fallback

```mermaid
sequenceDiagram
    participant Client as Client (sample_04_reranking.py)
    participant Proxy as inference_api.py (reverse_proxy)
    participant Backend as 8091 Reranker Backend (llama-server)

    Client->>Proxy: POST /v1/rerank
    Proxy->>Backend: POST http://127.0.0.1:8091/reranking
    alt /reranking Success (200 OK)
        Backend-->>Proxy: HTTP 200 OK (Rerank Scores)
        Proxy-->>Client: HTTP 200 OK
    else /reranking Returns 404
        Backend-->>Proxy: HTTP 404 Not Found
        Proxy->>Backend: Retry POST http://127.0.0.1:8091/v1/rerank
        Backend-->>Proxy: HTTP 200 OK (Rerank Scores)
        Proxy-->>Client: HTTP 200 OK
    end
```
