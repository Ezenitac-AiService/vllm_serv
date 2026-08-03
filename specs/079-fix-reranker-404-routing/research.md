# Technical Research & Design Decisions: `079-fix-reranker-404-routing`

**Feature Directory**: [`specs/079-fix-reranker-404-routing`](file:///home/dev/storage/vllm_serv/specs/079-fix-reranker-404-routing)  
**Spec**: [`spec.md`](spec.md)  

---

## 1. Technical Decisions

### Decision 1: `inference_api.py` 역방향 프록시 Reranker 경로 동적 번역 및 후보 탐색

- **Decision**: `src/api/routes/inference_api.py`의 `reverse_proxy` 함수에서 `clean_path in ("rerank", "reranking")` 처리 시 백엔드 8091 포트로 전송할 후보 앤드포인트 경로 목록 `["/reranking", "/v1/rerank", "/rerank", "/v1/reranking"]`을 구성합니다.
- **Rationale**: C++ `llama-server` (`--reranking` 옵션 지정 시 `/reranking` 노출) 및 `llama-cpp-python` 파이썬 모듈 등 다양한 백엔드 엔지니어링 구현체 간의 엔드포인트 경로 상이점을 동적으로 극복하여 404 Not Found 에러를 100% 방지합니다.
- **Alternatives Considered**: 
  - 백엔드 `llama-server` CLI 플래그 전면 수정 (C++ 바이너리의 고유 라우팅 규칙 변경 불가로 기각)

### Decision 2: HTTP 404 응답 시 비동기 후보 경로 자동 폴백 (Path Fallback Loop)

- **Decision**: 프록시 라우터가 첫 번째 후보 경로로 전송한 응답이 404인 경우, 즉시 다음 후보 경로로 재시도(Retry)하여 200 OK 응답을 반환하는 엔드포인트를 찾아 스트리밍 응답을 클라이언트로 반환합니다.
- **Rationale**: 클라이언트(`sample_04_reranking.py` 또는 사용자 RAG 시스템)가 어떤 URI (`/v1/rerank` 또는 `/rerank`)를 사용하더라도 백엔드 경로 차이에 영향받지 않고 100% 정상 작동을 보장합니다.
- **Alternatives Considered**: 단순 경로 리다이렉트 (POST 요청 body 재전송 문제로 기각)
