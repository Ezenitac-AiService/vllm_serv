# Data Model & State Transitions: `078-fix-samples-and-reranker-503`

**Feature Directory**: [`specs/078-fix-samples-and-reranker-503`](file:///home/dev/storage/vllm_serv/specs/078-fix-samples-and-reranker-503)  
**Spec**: [`spec.md`](spec.md) | **Research**: [`research.md`](research.md)  

---

## 1. Entities & Schema

### SampleServerConfig (샘플 클라이언트 서버 설정 엔티티)

| Entity Attribute | Type | Description | Constraints |
|------------------|------|-------------|-------------|
| `server_host` | String | 서빙 API 서버 URL (`http://10.0.0.41:8081` 또는 `http://192.168.0.100:8081`) | Valid HTTP URL string |
| `api_key` | String | API 인증 키 (선택사항) | String or null |
| `timeout_s` | Float | HTTP 통신 타임아웃 초 | Default 10.0 |

---

## 2. Sequence Diagram: Sample Client & On-Demand Reranker Routing

```mermaid
sequenceDiagram
    participant Client as Sample Script (sample_04_reranking.py)
    participant HostHelper as samples/common.py
    participant Proxy as Reverse Proxy (/v1/rerank)
    participant AuxMgr as AuxiliaryModelManager
    participant Backend as Reranker Backend (8091)

    Client->>HostHelper: get_server_host()
    HostHelper-->>Client: http://<config.json IP>:8081
    Client->>Proxy: POST http://<IP>:8081/v1/rerank
    Proxy->>AuxMgr: ensure_rerank_resident("bge-reranker-v2-m3")
    AuxMgr->>Backend: (Spawn / Poll 8091 if not ready)
    Backend-->>AuxMgr: 8091 READY (200 OK)
    AuxMgr-->>Proxy: ProcessState (READY)
    Proxy->>Backend: Forward POST /v1/rerank
    Backend-->>Proxy: HTTP 200 OK (Rerank Scores)
    Proxy-->>Client: HTTP 200 OK
```
