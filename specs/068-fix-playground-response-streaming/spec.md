# Feature Specification: AI Playground SSE 스트리밍 응답 렌더링 및 Qwen/DeepSeek 사고 과정 파싱 보장 (068-fix-playground-response-streaming)

**Feature Branch**: `068-fix-playground-response-streaming`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "못기다리고 서비스 플랫폼에서 db 파일 삭제하고 새로 구축했는데 db 파일 검증하는 스펙 구현은 그대로 진행하고 여전히 플레이그라운드가 제대로 대답 못함..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Playground SSE 스트리밍 응답 렌더링 및 Qwen/DeepSeek 사고 과정 파싱 (Priority: P1) 🎯 MVP

사용자가 웹 대시보드의 AI Playground에서 Qwen3.5, DeepSeek-R1 등 추론 모델에 질문을 전송하고 스트림 대답을 요청할 때, 사고 과정(`reasoning_content` / `<think>`)과 대답 텍스트가 빈 화면으로 남거나 사멸하지 않고 실시간 SSE 스트리밍으로 화면에 노출되어야 합니다.

**Why this priority**: AI Playground의 핵심 가치인 실시간 토큰 스트리밍과 사고 과정 시각화가 100% 정상 작동하도록 보장하는 핵심 기능입니다.

**Independent Test**: AI Playground UI 또는 `POST /dashboard/api/playground/stream` 엔드포인트 호출 시 SSE 데이터 청크(`think`, `text`, `metrics`)가 정상 전달되고 대답이 시각화되는지 100% 확인.

**Acceptance Scenarios**:

1. **Given** 백엔드에서 Qwen3.5 또는 DeepSeek 추론 모델이 상주 서빙 중일 때, **When** 사용자가 AI Playground에서 메시지를 전송하면, **Then** `reasoning_content`, `reasoning`, `content`, `text` 필드가 포함된 SSE 데이터 청크가 올바르게 파싱되어 UI에 렌더링되어야 합니다.
2. **Given** 백엔드 모델이 준비 중이거나 오프라인일 때, **When** 사용자가 AI Playground 스트리밍을 요청하면, **Then** 백엔드가 503 또는 모델 준비 중 안내 이벤트를 즉시 리턴하고 무한 대기하지 않아야 합니다.

---

### User Story 2 - MetricsDB 자동 복구 및 신규 구축 검증 테스트 (Priority: P2)

QA 및 개발자는 DB 파일 삭제 후 시스템 재구축 시에도 `MetricsDB` 지연 로딩 싱글톤과 시드 주입이 오류 없이 작동하는지 검증하길 원합니다.

**Why this priority**: DB 파일 수동 삭제/재구축 및 손상 자동 복구 파이프라인의 회귀 결함을 사전 차단합니다.

**Independent Test**: `uv run pytest tests/unit/test_metrics_db.py tests/unit/test_dashboard_api.py` 실행 시 100% Green Pass 통과.

### Edge Cases

- OpenAI 비표준 SSE 청크 형식(e.g., `delta.reasoning_content`만 포함되고 `content`가 `null`인 경우) 처리
- 백엔드 모델 로딩 시점 또는 타임아웃 예외 시 SSE 연결 자동 닫기 처리

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/api/routes/dashboard_api.py` 내 `run_playground_stream` 파서가 `reasoning_content` / `reasoning` / `content` / `text` 청크 필드를 모두 지원하여 Qwen/DeepSeek 모델 대답 무응답 방지
- **DoD-002**: `src/api/routes/dashboard_api.py` 내 `check_llama_status()` 사전 점검 추가로 모델 미준비 시 유저 안내 메시지 전달
- **DoD-003**: `src/core/metrics_db.py` DB 삭제/신규 재구축 후 Auto-Healing 및 `seed_db` 주입 정상 가동 검증
- **DoD-004**: 단위 및 회귀 테스트 수트 (`uv run pytest`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `src/api/routes/dashboard_api.py`는 SSE 스트리밍 청크 수신 시 OpenAI 호환 `reasoning_content`, `reasoning`, `content`, `text` 필드를 모두 파싱하여 생각 과정(`think`)과 답변(`text`)을 유저 UI로 실시간 노출해야 합니다.
- **FR-002**: `src/api/routes/dashboard_api.py`는 `run_playground_stream` 호출 시 백엔드 `llama-server` 엔진 가동 상태(`check_llama_status()`)를 사전 검증하여 모델 로딩/오프라인 상태 시 적절한 안내 이벤트를 전달해야 합니다.
- **FR-003**: `src/core/metrics_db.py`는 DB 파일 삭제 후 재생성 시 시드 주입(`seed_db`) 및 Auto-Healing 기능을 안전하게 수행해야 합니다.

### Key Entities

- **PlaygroundStreamChunk**: `reasoning_content`, `content`, `text` 토큰 조각을 포함하는 SSE 스트리밍 데이터 구조
- **MetricsDBInstance**: DB 파일 복구 및 지연 싱글톤 관리를 수행하는 데이터베이스 매니저

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI Playground SSE 스트리밍 구동 시 대답 텍스트 및 사고 과정 전달 성공률 100%
- **SC-002**: 전체 pytest 회귀 테스트 통과율 100%

## Assumptions

- 백엔드 인퍼런스 엔진 `llama-server`는 표준 OpenAI `/v1/chat/completions` 스트리밍 API 규격을 따릅니다.
- 추론 모델의 사고 과정 토큰은 `<think>...</think>` 태그 또는 `reasoning_content` JSON 필드로 전달됩니다.
