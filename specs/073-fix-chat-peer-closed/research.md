# Phase 0 Research: Chat Completions API 커넥션 두절 (Content-Length Mismatch) 오류 및 서빙 파이프라인 최적화

## Overview

본 연구 문서에서는 `vllm_serv` 플랫폼의 Chat Completions API (`/v1/chat/completions`, port 8081) 호출 시 발생하던 `h11.LocalProtocolError: Too little data for declared Content-Length` 예외와 이로 인한 `peer closed connection without sending complete message body` 오류를 분석하고, 2026년 8월 최신 LLM ASGI 서빙 규격에 맞는 해결 방안 및 기술적 결정을 정의합니다.

## Research Findings & Technical Decisions

### Decision 1: FastAPI/Starlette/Uvicorn 응답 파이프라인의 Content-Length & Chunked Encoding 정합성 확보

- **Problem**:
  `sample_01_chat.py` 및 `sample_02_model_params.py` 실행 시 역방향 프록시 또는 API 응답 핸들러에서 사전 설정된 `Content-Length` 헤더의 바이트 크기와 실제 전송되는 응답 바디(JSON 스트링)의 바이트 크기가 일치하지 않는 현상 발생. (특히 UTF-8 한글 멀티바이트 문자 수 vs 바이트 수 불일치 또는 Stop sequence 감지 시 바디 송신 조기 종료). Uvicorn의 `h11` HTTP 프로토콜 래퍼가 이를 감지하여 `LocalProtocolError("Too little data for declared Content-Length")`를 발생시키고 ASGI 커넥션을 강제로 닫음.

- **Decision**:
  1. **Non-Streaming JSON 응답**: FastAPI 기본 `JSONResponse` 직렬화를 사용하거나, 커스텀 헤더 부여 시 반드시 `len(body_bytes)` (UTF-8 encoded byte count) 기반으로 `Content-Length`를 자동 계산하도록 보장.
  2. **Streaming & Stop-Sequence 응답**: `StreamingResponse` 사용 시 사전 고정 `Content-Length` 헤더를 명시적으로 제거(Omit)하고 `Transfer-Encoding: chunked`를 표준 적용하며, 토큰 생성이 중단되거나 완료될 때 최종 EOF(Empty chunk `b""`)를 안전하게 수반하여 송신 완료 신호를 Uvicorn에 전하여 커넥션 두절 방지.

- **Alternatives Considered**:
  - *Keep-Alive 타임아웃 연장*: 원인이 소켓 타임아웃이 아니라 HTTP 프로토콜 바디 자릿수 미달 예외이므로 효과 없음.
  - *Silent Error Catching*: 헌법 II조 (Zero-Mock & Fake Green 금지) 위반이므로 배제.

---

### Decision 2: 8091 포트 BGE Reranker v2 M3 서빙 데몬 바인딩 및 모니터링 동기화

- **Problem**:
  `sample_04_reranking.py` 실행 시 포트 8091 (BGE Reranker v2 M3) 연결 실패 발생.

- **Decision**:
  - `start_server.sh` 및 `AuxiliaryManager`에서 BGE Reranker 프로세스(port 8091) 구동 상태를 명확히 확인하고, `status_server.sh` 헬스 체크 모니터링 대상 포트에 8091을 동기화하여 멀티 모델 독립 포트 서빙을 완성함.

- **Rationale**:
  Chat(8081), Embedding(8090), Reranking(8091) 서빙 데몬이 독립 포트로 안정적으로 격리 운용됨을 보장.

---

### Decision 3: Zero-Mock 기반 실체적 TDD 수렴 검증 체계 확립

- **Decision**:
  - 헌법 II조 및 III조(Zero Mock & Real Integration 원칙)에 부합하도록 실제 `llama-server` 백엔드 프로세스 및 Uvicorn ASGI 파이프라인의 실측 통합 테스트(`tests/integration/test_chat_connection.py`)를 수록하고 `uv run pytest`로 100% 그린 검증.

## Summary of Architecture Choices

1. **Protocol Stack**: Python 3.12 + FastAPI + Uvicorn (h11) + httpx
2. **Streaming Encoding**: HTTP/1.1 Chunked Transfer Encoding & UTF-8 Byte Length Calculation
3. **Serving Ports**: 8081 (Chat), 8090 (Embedding), 8091 (Reranker)
