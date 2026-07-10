# Phase 0: Research & Technical Decisions

- Decision: Server-Sent Events (SSE) via `EventSourceResponse` in FastAPI
- Rationale: Polling is 비효율적(inefficient) for 60-second loading tasks. SSE allows pushing real-time load/unload status and VRAM updates with minimal overhead.
- Alternatives considered: WebSockets (양방향 통신 오버킬), Polling (자원 낭비 및 지연 발생).

- Decision: Graceful Degradation using 503 Maintenance Mode Middleware
- Rationale: 모델 리로드 중 발생하는 60초의 공백 시간 동안 들어오는 추론 요청(`/v1/...`)은 무한 대기(Timeout)되거나 에러를 뿜습니다. FastAPI 미들웨어나 의존성 주입을 통해 현재 모델 상태가 READY가 아니면 즉각 `503 Service Unavailable`과 `Retry-After: 30` 헤더를 반환하여 클라이언트 측 예외 처리를 유도합니다.
- Alternatives considered: Request Queuing (복잡도 증가, VRAM 고갈 위험).

- Decision: Vanilla JS + CSS (정적 파일 서빙)
- Rationale: 복잡한 프론트엔드 빌드 파이프라인(Node.js, Webpack) 없이 FastAPI의 `StaticFiles`를 통해 즉시 서빙 가능하도록 가벼운 Vanilla JS로 구현합니다. CSS는 모던 Glassmorphism UI를 적용하여 고급스러운 관리자 경험을 제공합니다.
- Alternatives considered: React/Vue (설정 오버헤드 큼).
