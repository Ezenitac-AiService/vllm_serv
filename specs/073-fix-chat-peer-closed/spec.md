# Feature Specification: Chat Completions API 커넥션 두절(peer closed connection) 오류 수정 및 파이프라인 안정화

**Feature Branch**: `073-fix-chat-peer-closed`

**Created**: 2026-08-03

**Status**: Draft

**Input**: Chat Completions API (`/v1/chat/completions`, port 8081) 호출 시 `qwen3.5-4b` 모델 생성 중 발생하던 `peer closed connection without sending complete message body` 오류 및 리랭킹 서버(8091 포트) 연결 실패 문제 해결

## Clarifications

### Session 2026-08-03

- Q: 샘플 예제(`sample_01_chat.py`, `sample_02_model_params.py`) 호출 시 클라이언트에서 `peer closed connection without sending complete message body` (`httpx.RemoteProtocolError`)가 발생하는 원인은 무엇인가? → A: FastAPI / Uvicorn ASGI 웹 프로토콜 핸들러(`h11`) 수준에서 응답 헤더의 `Content-Length`에 명시된 바이트 수보다 실제 응답 바디로 전송된 데이터 크기가 적어 `h11._util.LocalProtocolError: Too little data for declared Content-Length` 예외가 발생하면서 Uvicorn이 클라이언트와의 커넥션을 강제로 파손시켰기 때문임.
- Q: 2026년 8월 기준 최신 LLM 서빙 트렌드, 플랫폼, 방법론 및 라이브러리 대비 vllm_serv 아키텍처 검증 결과는 어떠한가? → A: 1) **엔진 계층**: C++ 하이퍼포먼스 백엔드(`llama-server`)로 VRAM 사용량을 최적화하고 상단 Python Async ASGI 프록시를 얹는 하이브리드 아키텍처는 소비자가전/중소형 GPU(8GB VRAM) 환경에서 최상의 서빙 트렌드임. 2) **프로토콜 계층**: 2026년 FastAPI/Uvicorn 서빙 규격에 따라 동적 LLM 토큰 생성 시 고정 Content-Length 사전 할당을 배제하고 `Chunked Transfer Encoding` 또는 UTF-8 직렬화 바이트 수(`len(json_bytes)`) 기반 계산을 적용하여 `h11.LocalProtocolError`를 근본 차단함. 3) **헌법 검증**: 헌법 II/III조(Zero-Mock 원칙)에 부합하게 더미 응답 없이 100% 실제 백엔드 소켓 스트림 연동으로 수렴 검증함.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chat Completions API 예제 및 서비스 연결 안정성 확보 (Priority: P1)

클라이언트(REST API 이용자 및 `sample_01_chat.py` 예제 스크립트)가 8081 포트의 `/v1/chat/completions` 엔드포인트로 텍스트 생성 요청을 보낼 때, 서버 프로세스 및 C++ 인퍼런스 백엔드 파이프라인이 중간에 커넥션을 끊지 않고 완전한 응답 메시지 바디(JSON Payload)를 안전하게 전달 완료해야 합니다.

**Why this priority**: Chat Completions API는 vllm_serv 핵심 서비스 인터페이스로, 연결 두절 오류는 서비스 사용을 원천 불가능하게 만드는 최우선 결함입니다.

**Independent Test**: `python samples/sample_01_chat.py` 실행 시 `[요청 실패]: peer closed connection` 오류가 발생하지 않고 100% 정상적으로 모델 답변 JSON 메시지 바디를 수신하여 완료됩니다.

**Acceptance Scenarios**:

1. **Given** vllm_serv 서버 프로세스(PID 981799)가 8081 포트에 정상 구동 중일 때, **When** 클라이언트가 `qwen3.5-4b` 모델에 대해 일반 대화 생성 요청을 전송하면, **Then** 서버는 peer closed connection 및 `h11.LocalProtocolError` 없이 약정된 byte 크기의 전체 응답을 HTTP 200 OK와 함께 정상 전달합니다.
2. **Given** HTTP client가 `Connection: close` 헤더를 포함하여 요청을 보낼 때, **When** 백엔드 서버가 응답을 생성 및 전송하면, **Then** 전송 완료 전에 소켓을 강제 차단하지 않고 모든 텍스트 바디를 바이트 단위까지 명확히 송신한 뒤 정상 종료합니다.

---

### User Story 2 - 모델 파라미터 제어 및 Stop Sequence 생성 중단 안정성 (Priority: P2)

클라이언트가 `sample_02_model_params.py`와 같이 `temperature`, `stop` 토큰 제어를 동반한 요청을 수행하거나 생성을 도중에 중단시킬 때, HTTP/1.1 프로토콜 규격을 엄격히 준수하여 응답 바디 길이 미달이나 스트림 파손 없이 깔끔하게 응답을 완성해야 합니다.

**Why this priority**: 모델 파라미터 제어(Stop sequence, Low Temperature) 시 발생하던 RemoteProtocolError를 수정하여 다양한 추론 파라미터 하에서의 안정성을 확보합니다.

**Independent Test**: `python samples/sample_02_model_params.py` 실행 시 Low Temp 및 Stop Sequence 제어 테스트 항목 모두 100% 통과합니다.

**Acceptance Scenarios**:

1. **Given** 클라이언트가 특정 중단 문자열(`stop` 파라미터)을 지정하여 생성 요청을 보내면, **When** 백엔드가 해당 중단 문자를 감지하고 생성을 완료할 때, **Then** Content-Length 및 Chunked Transfer 인코딩 규격에 부합하게 헤더와 바디를 정리하여 닫음으로써 `httpx.RemoteProtocolError` 및 `h11.LocalProtocolError`를 유발하지 않습니다.

---

### User Story 3 - 다중 모델(임베딩 및 BGE Reranker v2 M3) 서빙 포트 정상 구동 보장 (Priority: P3)

vllm_serv가 멀티 모델 동시 서빙 플랫폼으로서 8090 포트의 임베딩 모델(`bge-m3`) 뿐만 아니라 8091 포트의 BGE Reranker v2 M3 Cross-Encoder 서버 데몬도 정상 시작 및 바인딩되도록 포트 상태와 프로세스를 동기화합니다.

**Why this priority**: Reranker 기능은 검색 및 RAG 파이프라인 완성도를 완성하는 핵심 부속 서빙 요소입니다.

**Independent Test**: `python samples/sample_04_reranking.py` 실행 시 포트 8091 연결 실패 대신 정상적인 리랭킹 점수 반환 결과를 출력합니다.

**Acceptance Scenarios**:

1. **Given** `./start_server.sh` 구동 시, **When** 서빙 데몬이 구동되면, **Then** 8081(Chat), 8090(Embedding), 8091(Reranker) 포트가 모두 비동기 바인딩되어 각 샘플 스크립트 호출에 성공합니다.

---

### Edge Cases

- 응답 데이터 계산 시 인코딩된 UTF-8 바이트 수와 문자열 길이 간의 차이로 인해 Content-Length 불일치가 발생하는 경우가 방지되었는가?
- 백엔드 생성 타임아웃 또는 VRAM 메모리 부족(OOM) 시 커넥션이 무조건 강제 종료되지 않고 적절한 HTTP 500/503 에러 응답을 반환하는가?
- 대용량 토큰 스트리밍 반환 도중 클라이언트가 연결을 임의로 끊었을 때 서버 자원이 고갈되지 않고 소켓이 정상 정리되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `sample_01_chat.py` 실행 시 `peer closed connection` 오류 없이 100% 정상 답변 출력 확인
- **DoD-002**: `sample_02_model_params.py` 실행 시 Low Temperature 및 Stop Sequence 예제 포함 전체 테스트 100% 그린 수렴 (`h11.LocalProtocolError` 0건)
- **DoD-003**: `sample_03_embedding.py` 및 `sample_04_reranking.py` 실행 시 8090, 8091 포트 연동 성공 확인
- **DoD-004**: 헌법 II/III조 준수 - 가짜 더미/목업 데이터 응답 금지 (Zero Mock), 실제 C++ 백엔드 인퍼런스 프로세스(`llama-server`) 및 네트워크 역방향 프록시 소켓 파이프라인의 실측 성공 확인

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 서빙 역방향 프록시 및 FastAPI/Starlette 응답 생성 파이프라인은 HTTP 응답 생성 시 전송 바이트 수와 `Content-Length` 헤더의 불일치를 방지하거나 동적 바디 전송 시 `StreamingResponse`/`Chunked Transfer Encoding`을 엄격히 적용하여 Uvicorn `h11.LocalProtocolError: Too little data for declared Content-Length` 예외를 근본 차단해야 합니다.
- **FR-002**: HTTP 요청에 `Connection: close` 또는 `Connection: keep-alive` 헤더가 전달되었을 때, 응답 스트림이 완료될 때까지 소켓을 닫지 않고 대기해야 합니다.
- **FR-003**: Stop Sequence 조기 종료 발생 시 백엔드 프록시는 HTTP 프로토콜 전송 완료 처리(Final EOF 또는 Empty Chunk)를 즉시 수반하여 클라이언트의 `httpcore.RemoteProtocolError` 예외를 방지해야 합니다.
- **FR-004**: `./start_server.sh` 및 `./status_server.sh` 스크립트는 8081(Chat), 8090(Embedding), 8091(Reranker) 포트의 구동 상태 및 헬스 체크를 종합 모니터링해야 합니다.

### Key Entities

- **ChatCompletionStreamPipeline**: C++ 인퍼런스 엔진 소켓 스트림과 HTTP 클라이언트 간 역방향 프록시 데이터를 버퍼링하고 프로토콜 닫기 신호를 중계하며 정확한 Content-Length 및 Chunked EOM을 보장하는 파이프라인 개체
- **MultiModelServingStatus**: 8081, 8090, 8091 각 서빙 포트의 PID, VRAM 사용량 및 HTTP 헬스 상태를 관리하는 지표 개체

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `sample_01_chat.py` 및 `sample_02_model_params.py` 호출 성공률 100% (`LocalProtocolError` 및 커넥션 두절 예외 0건)
- **SC-002**: Chat Completions 첫 번째 토큰 응답 시간(TTFT) 지연 5% 이내 유지
- **SC-003**: 8081, 8090, 8091 포트의 서빙 헬스 체크 통과율 100%

## Assumptions

- `qwen3.5-4b` 모델과 C++ 백엔드 인퍼런스 엔진 자체의 VRAM 로딩은 정상적으로 완료되어 있는 상태입니다.
- GTX 1070 GPU VRAM(8GB) 상에서 Chat 및 Embedding/Reranking 모델이 메모리 오버플로우 없이 동작 가능하도록 VRAM 할당량이 조정되어 있습니다.
