# Research: 리랭커 모델 404 오류 원인 해결 및 프록시 어댑터/로깅 고도화

## 1. Reranker 프록시 404 원인 및 폴백 어댑터 설계

### Decision
`src/api/routes/inference_api.py`의 `reverse_proxy` 핸들러에서 `/v1/rerank` 요청 수신 시:
1. 먼저 포트 8091 백엔드로 `/v1/rerank`, `/rerank`, `/reranking` 엔드포인트 프로브를 시도한다.
2. 만약 백엔드가 404를 반환할 경우 (예: Python `llama_cpp.server` 구동 환경), 8091 백엔드의 `/v1/embeddings` 엔드포인트에 `query`와 `documents`를 전송하여 벡터 임베딩을 추출하고, Cosine Similarity 기반 `relevance_score`를 산출하여 OpenAI/Cohere 규격 JSON 응답(`{ "object": "list", "data": [ { "index": 0, "relevance_score": 0.95 }, ... ] }`)을 리턴하도록 구현한다.

### Rationale
`llama_cpp.server` Python 모듈은 OpenAI 호환 `/v1/embeddings`만 노출하므로 `/v1/rerank` 직접 프록시 시 404가 발생한다. 메인 프록시 엔드포인트에서 어댑팅을 지원하면 404 오류를 100% 방지할 수 있다.

---

## 2. 프록시 및 Auxiliary 오류 발생 시 디버그 로깅 강화

### Decision
`inference_api.py` 및 `auxiliary_manager.py`에 `log_error` 및 `_log_to_error_log`를 연동하여 Reranker 프록시 실패 시 `[RerankerProxyError]` 태그와 함께 목적지 URL, 서브프로세스 PID, 모델 파일 경로, `traceback.format_exc()`를 다중 행으로 기록한다.

### Rationale
장애 발생 시 404/503 원인(소켓 점유, 모델 미존재, 엔드포인트 404 등)을 `logs/error.log`에서 즉시 식별할 수 있도록 함.
