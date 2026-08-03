# Data Model & Domain Entities: Chat Completions API 파이프라인

## Domain Entities

### 1. ChatCompletionRequest (대화 생성 요청 엔티티)

OpenAI REST API 규격과의 100% 호환성을 보장하는 Chat Completions 요청 모델입니다.

| Attribute | Type | Required | Description | Constraints |
| :--- | :--- | :---: | :--- | :--- |
| `model` | String | Yes | 대상 LLM 서빙 모델명 (예: `qwen3.5-4b`) | Non-empty |
| `messages` | List[Dict] | Yes | 대화 히스토리 목록 (`role`, `content`) | Minimum 1 message |
| `temperature` | Float | No | 샘플링 무작위성 (기본값: 0.7) | 0.0 <= temp <= 2.0 |
| `top_p` | Float | No | 누적 확률 샘플링 (기본값: 1.0) | 0.0 <= top_p <= 1.0 |
| `stop` | Union[String, List] | No | 생성을 조기 중단할 단어/토큰 배열 | Max 4 stop sequences |
| `stream` | Boolean | No | 스트리밍 응답 여부 (기본값: False) | True / False |

---

### 2. ChatCompletionResponse (대화 생성 응답 엔티티)

Non-streaming 대화 생성 최종 JSON 응답 모델입니다.

| Attribute | Type | Description | Content-Length Target |
| :--- | :--- | :--- | :--- |
| `id` | String | 요청 고유 식별자 (`chatcmpl-xxx`) | Exact UTF-8 Byte Count |
| `object` | String | 객체 유형 (`chat.completion`) | Exact UTF-8 Byte Count |
| `created` | Integer | 생성 유닉스 타임스탬프 | Exact UTF-8 Byte Count |
| `model` | String | 실제 실행된 서빙 모델명 | Exact UTF-8 Byte Count |
| `choices` | List[Dict] | 생성 결과 메세지 및 finish_reason | `stop` / `length` 값 포함 |
| `usage` | Dict | 토큰 사용 통계 (prompt/completion/total) | Integer metrics |

---

### 3. StreamResponseChunk (스트리밍 파이프라인 청크)

HTTP `Transfer-Encoding: chunked` 전송 시 사용되는 개별 SSE 스트림 단위 엔티티입니다.

| Attribute | Type | Description | Protocol Rule |
| :--- | :--- | :--- | :--- |
| `delta` | Dict | 새로 생성된 토큰 텍스트 조각 | SSE `data: {...}` 포맷 |
| `finish_reason` | Optional[String] | 완료 사유 (`stop`, `length` 또는 null) | 마지막 청크에 포함 |
| `is_final` | Boolean | 스트림 종료 여부 | True 시 `data: [DONE]` 전송 |

---

### 4. ServingPortStatus (다중 서빙 포트 지표 엔티티)

| Attribute | Type | Port | Health Rule |
| :--- | :--- | :---: | :--- |
| `chat_service` | Dict | 8081 | GET `/health` HTTP 200 & PID Alive |
| `embedding_service` | Dict | 8090 | GET `/v1/embeddings` HTTP 200 |
| `reranker_service` | Dict | 8091 | BGE Reranker v2 M3 HTTP 200 |
