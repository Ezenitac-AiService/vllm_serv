# Feature Specification: Reranker API `/v1/rerank` 404 라우팅 오류 해결 (`079-fix-reranker-404-routing`)

**Feature Directory**: [`specs/079-fix-reranker-404-routing`](file:///home/dev/storage/vllm_serv/specs/079-fix-reranker-404-routing)  
**Created**: 2026-08-03  
**Status**: Draft  

---

## 1. Overview & Business Value

`vllm_serv` 메인 API 서버(포트 8081)로 Reranker 엔드포인트 요청(`POST /v1/rerank` 또는 `POST /rerank`)을 전송할 때, 8091 보조 백엔드 엔진(`llama-server` / `llama-cpp-python`)의 실제 엔드포인트 경로 차이로 인해 발생하는 `404 Not Found` 라우팅 오류를 근본적으로 수정합니다.

`src/api/routes/inference_api.py`의 역방향 프록시 라우터에서 `/v1/rerank` 요청 수신 시, 백엔드 엔진이 제공하는 앤드포인트 경로(`/reranking`, `/v1/rerank`, `/rerank`, `/v1/reranking`)를 동적으로 폴백/번역(Path Translation)하여 404 에러를 100% 방지하고 정상 200 OK 재순위화 결과를 리턴하도록 수정합니다.

---

## 2. User Personas & Scenarios

- **Persona**: AI 애플리케이션 개발자 / 교육생 / RAG 서비스 연동 시스템
- **Scenario**:
  1. 개발자 또는 예제 스크립트(`sample_04_reranking.py`)가 `POST http://<server>:8081/v1/rerank`를 호출할 때, 백엔드 포트 8091 데몬이 C++ `llama-server` (`/reranking`) 또는 파이썬 모듈이든 관계없이 404 에러 없이 200 OK와 리랭킹 결과를 정상 수신합니다.
  2. 프록시 라우터가 백엔드 8091 데몬으로 요청 전달 시 404 응답을 받으면, 보조 후보 경로(`/reranking`, `/v1/reranking`, `/rerank`)를 자동으로 탐색하여 실패 없이 응답을 완료합니다.

---

### User Story 1 - Reranker API 역방향 프록시 앤드포인트 자동 번역 및 404 폴백 해결 (Priority: P1)

`POST /v1/rerank` 및 `POST /rerank` 요청 수신 시, 백엔드 포트 8091 데몬의 호환 가능한 엔드포인트 경로를 자동으로 번역/폴백 탐색하여 `404 Not Found` 예외를 차단해야 합니다.

**Why this priority**: RAG 파이프라인 및 문서 재순위화(Reranking) 서비스의 가용성 및 파이프라인 신뢰성을 보장하는 최우선 요구사항입니다.

**Independent Test**: 8091 백엔드 데몬이 `/reranking` 또는 `/v1/rerank` 엔드포인트를 제공할 때, `POST http://127.0.0.1:8081/v1/rerank` 및 `sample_04_reranking.py` 호출 시 404 에러 없이 HTTP 200 OK 응답 및 점수를 수신하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 8081 메인 API 서버 구동 상태에서, **When** `sample_04_reranking.py` 또는 `POST /v1/rerank` 요청을 전송하면, **Then** 404 Not Found 에러가 발생하지 않고 HTTP 200 OK 및 재순위화 점수가 정상 반환됩니다.
2. **Given** 8091 백엔드 엔진이 `/reranking` 엔드포인트를 노출하고 있을 때, **When** 클라이언트가 `/v1/rerank`로 요청하면, **Then** 프록시 라우터가 경로를 자동 번역 및 폴백하여 200 OK 응답을 전달합니다.

---

### Edge Cases

- **모든 후보 백엔드 경로 실패**: `/reranking`, `/v1/rerank`, `/rerank`, `/v1/reranking` 전체에 대해 404 반환 시에만 404 예외 리턴 및 명확한 가이드 메시지 포함.
- **Reranker 백엔드 데몬 미가동**: 503 Service Unavailable 및 `auxiliary_manager.ensure_rerank_resident()` 온디맨드 구동 유지.

---

## 3. Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/api/routes/inference_api.py` 역방향 프록시가 Reranker 요청 시 백엔드 포트 8091의 `/reranking`, `/v1/rerank`, `/rerank` 후보 경로를 자동 번역/폴백 처리해야 함.
- **DoD-002**: `python samples/sample_04_reranking.py` 스크립트 실행 시 `404 Not Found` 에러 0건 및 100% 정상 실행(HTTP 200 OK)되어야 함.
- **DoD-003**: 통합 테스트 수트(`tests/integration/test_reranker_404_routing.py`) 작성 및 통과.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Reranker 프록시 경로 번역 및 폴백)**: `src/api/routes/inference_api.py`의 `reverse_proxy`는 Rerank 요청 처리 시 백엔드 8091 포트에 대해 후보 경로(`["/reranking", "/v1/rerank", "/rerank", "/v1/reranking"]`)를 자동 탐색/전환하여 404 오류를 방지해야 한다.
- **FR-002 (OpenAI 규격 호환 보장)**: 클라이언트가 `/v1/rerank` 및 `/rerank` 두 경로 모두로 요청 가능하도록 FastAPI 라우트 및 프록시 호환성을 유지해야 한다.

---

## 5. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `python samples/sample_04_reranking.py` 실행 시 404 에러 발생률 0%.
- **SC-002**: `/v1/rerank` 요청에 대한 200 OK 응답 성공률 100%.

---

## 6. Assumptions

- 8091 포트는 BGE Reranker v2 M3 전용 데몬으로 구동됩니다.
- C++ `llama-server`의 Reranking 엔드포인트는 `--reranking` 옵션 지정 시 `/reranking` 또는 `/v1/rerank`로 수신합니다.
