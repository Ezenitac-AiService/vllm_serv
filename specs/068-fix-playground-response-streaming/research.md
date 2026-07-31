# Research: AI Playground SSE 스트리밍 응답 렌더링 및 Qwen/DeepSeek 사고 과정 파싱 보장 (068-fix-playground-response-streaming)

**Feature**: `068-fix-playground-response-streaming`

## Technical Decisions & Rationale

### Decision 1: SSE 스트리밍 청크 내 `reasoning_content` / `reasoning` 필드 동적 수용
- **선택된 방식**: `src/api/routes/dashboard_api.py` 내 `run_playground_stream` 제너레이터에서 `delta.get("reasoning_content")` 및 `delta.get("reasoning")` 토큰 조각을 감지하여 `event: think_start` / `event: think_end` 및 `data: {"think": ...}` 조각으로 전송.
- **이유**: Qwen3.5 및 DeepSeek-R1 등 최신 추론 LLM 모델은 사고 과정 토큰을 OpenAI 호환 `reasoning_content` 필드로 반환하므로, 기존 `delta.get("content")` 전용 파서에서 토큰이 유실되어 플레이그라운드 대답이 빈 화면으로 렌더링되던 문제를 근본적으로 해결합니다.

### Decision 2: 백엔드 인퍼런스 엔진 가동 상태 사전 검증 (`check_llama_status()`)
- **선택된 방식**: `run_playground_stream` 엔드포인트 진입 시 `await check_llama_status()`를 호출하여 모델 로딩/오프라인 상태 시 503/유저 메시지 SSE 이벤트를 즉시 전달하고 스트림을 반환.
- **이유**: 엔진 로딩 중 유저가 스트리밍을 요청하였을 때 연결이 무한 대기하거나 빈 응답으로 즉시 종료되는 현상을 방지합니다.

### Decision 3: SQLite MetricsDB 자동 복구 및 안전 시드 주입
- **선택된 방식**: DB 파일 삭제 후 재배포 시 `MetricsDB` 생성을 지연 싱글톤 `_LazyMetricsDBProxy` 및 `get_metrics_db()`로 유지하고, `seed_db` 주입 및 auto-healing 방어책을 정립함.
- **이유**: 서비스 디스크 상의 DB 파일 손상/삭제 시에도 모듈 import 시점의 파이썬 인터프리터 사멸을 차단하고 안정적인 복구를 보장합니다.
