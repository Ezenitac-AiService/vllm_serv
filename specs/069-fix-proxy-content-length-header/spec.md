# Feature Specification: Inference API Reverse Proxy Content-Length Header Handling Fix (069-fix-proxy-content-length-header)

**Feature Branch**: `069-fix-proxy-content-length-header`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "LocalProtocolError: Too little data for declared Content-Length in uvicorn/h11_impl.py, sample_01_chat.py failed with peer closed connection without sending complete message body"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reverse Proxy 응답 헤더 필터링 및 정상 통신 보장 (Priority: P1) 🎯 MVP

클라이언트 개발자 및 RAG 마이크로서비스가 `POST /v1/chat/completions` 또는 `sample_01_chat.py` 예제 스크립트를 실행할 때, 백엔드 LLM 엔진의 헤더 중 `content-length`가 `StreamingResponse`로 오전달되어 Uvicorn `h11` 프로토콜 에러(`LocalProtocolError: Too little data for declared Content-Length`)가 발생하거나 연결이 끊어지지 않고 전체 대답 텍스트를 정상 수신해야 합니다.

**Why this priority**: REST API 추론 파이프라인의 전체 안정성을 결정짓는 핵심 결함 수정입니다.

**Independent Test**: `/v1/chat/completions` 엔드포인트 호출 및 `sample_01_chat.py` 실행 시 100% 정상 HTTP 200 응답 및 완료 본문 수신 검증.

**Acceptance Scenarios**:

1. **Given** `vllm_serv` 백엔드 엔진이 구동 중일 때, **When** 클라이언트가 `POST /v1/chat/completions`에 비스트림 요청을 전송하면, **Then** `Content-Length` 충돌 없이 200 OK와 완결된 JSON 응답이 반환되어야 합니다.
2. **Given** 클라이언트가 스트리밍 또는 비스트리밍 요청을 전송할 때, **When** 백엔드 응답 헤더에 `content-length`, `transfer-encoding` 등이 포함되어 있어도, **Then** `reverse_proxy`가 해당 헤더를 안전하게 제거하고 클라이언트에 전달해야 합니다.

---

### User Story 2 - 헤더 필터링 단위 테스트 및 회귀 검증 (Priority: P2)

QA 및 개발자는 회귀 테스트 수트를 통해 reverse proxy 헤더 처리 로직이 향후 커밋에서도 안정적으로 동작함을 보장받고자 합니다.

**Why this priority**: API 게이트웨이 역방향 프록시 헤더 처리 로직의 재발을 방지합니다.

**Independent Test**: `uv run pytest tests/unit/test_inference_api_proxy_headers.py` 실행 시 100% Green Pass 통과.

### Edge Cases

- 백엔드 응답에 `content-length`, `transfer-encoding`, `content-encoding` 헤더가 대소문자 무관하게 존재하는 경우 필터링
- 에러 응답(4xx, 5xx) 반환 시에도 안전한 헤더 필터링 적용

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/api/routes/inference_api.py` 내 `reverse_proxy` 응답 헤더 생성 시 `content-length`, `transfer-encoding`, `content-encoding`, `connection` 제어 헤더 제외 필터링 적용
- **DoD-002**: `sample_01_chat.py` 실행 시 `LocalProtocolError` 없이 100% 정상 수신 확인
- **DoD-003**: 단위 테스트 작성 및 전체 회귀 테스트(`uv run pytest`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `src/api/routes/inference_api.py`의 `reverse_proxy`는 백엔드 서버 응답 헤더(`r.headers`) 중 `content-length`, `transfer-encoding`, `content-encoding`, `connection`을 제거한 헤더 딕셔너리로 `StreamingResponse`를 생성해야 합니다.
- **FR-002**: `src/api/routes/inference_api.py`는 스트리밍 및 비스트리밍 `/v1/chat/completions`, `/v1/embeddings`, `/v1/rerank` 요청에서 Uvicorn `h11` 프로토콜 충돌을 차단해야 합니다.

### Key Entities

- **FilteredResponseHeaders**: `content-length`, `transfer-encoding`, `content-encoding`, `connection` 키가 제외된 프록시 응답 헤더 딕셔너리

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `sample_01_chat.py` 및 OpenAI API 호출 시 `LocalProtocolError: Too little data for declared Content-Length` 에러 발생률 0%
- **SC-002**: 전체 pytest 회귀 테스트 통과율 100%

## Assumptions

- FastAPI/Starlette의 `StreamingResponse`는 본문 전송 시 `Transfer-Encoding: chunked`를 자체 관리하므로 상위 헤더의 `Content-Length`가 존재하면 `h11` 라이브러리와 충돌합니다.
