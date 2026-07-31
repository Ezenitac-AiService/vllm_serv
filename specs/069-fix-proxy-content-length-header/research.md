# Research: Inference API Reverse Proxy Content-Length Header Handling Fix (069-fix-proxy-content-length-header)

**Feature**: `069-fix-proxy-content-length-header`

## Technical Decisions & Rationale

### Decision 1: Reverse Proxy 응답 생성 시 Hop-by-Hop 및 길이 관련 헤더 필수 제외
- **선택된 방식**: `src/api/routes/inference_api.py` 내 `reverse_proxy` 반환 시 `excluded_headers = {"content-length", "transfer-encoding", "connection", "content-encoding"}` 딕셔너리 필터링 적용.
- **이유**: FastAPI `StreamingResponse`는 Chunked Transfer Encoding으로 수신된 스트림을 클라이언트에 전달하는데, 백엔드의 고정 `Content-Length`가 포함되어 있을 경우 Uvicorn `h11` HTTP 라이브러리가 "선언된 길이보다 전송된 데이터가 적다"며 `LocalProtocolError`를 발생시키고 TCP 소켓을 닫는 문제를 근본적으로 차단합니다.

### Decision 2: 대소문자 구분 없는 (Case-Insensitive) 헤더 키 필터링
- **선택된 방식**: `r.headers.items()` 순회 시 `k.lower() not in excluded_headers`로 대소문자 독립적 검증 수행.
- **이유**: HTTP/1.1 및 HTTP/2 헤더 키는 `Content-Length`, `content-length`, `TRANSFER-ENCODING` 등 다양한 케이스로 반환될 수 있으므로 `k.lower()` 소문자 정규화 필터링이 필요합니다.
