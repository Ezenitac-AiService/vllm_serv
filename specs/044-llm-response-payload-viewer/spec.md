# Feature Specification: LLM 프롬프트 및 대답 응답 내용 (Inference Payload) 저장 & Google AI Studio 스타일 대화형 플레이그라운드 고도화 (044-llm-response-payload-viewer)

**Feature Branch**: `044-llm-response-payload-viewer`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User report: "Google AI Studio 및 OpenAI Playground 2026 레퍼런스 기준 AI Playground 대화형 UI/UX 고도화 (Chat Thread, System Instruction Side Panel, SSE Streaming Animation, Metric Chips, Code Export Toolbar) 및 LLM 대답 원문 Payload 시각 뷰어 구현."

---

## Clarifications

### Session 2026-07-30

- Q: 플레이그라운드 대화 레이아웃 UI/UX 구조 (Google AI Studio & OpenAI Playground Style) → A: Option A - Google AI Studio 2026 Style (Chat Thread 메인 캔버스 + Side Parameter Panel + SSE Streaming & Code Export Bar 일체형 구현)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Google AI Studio Style 2026 대화형 플레이그라운드 UI/UX 고도화 (Priority: P1) 🎯 MVP

웹 대시보드 "AI Playground" 탭을 **[메인 Chat Thread 대화 창]**과 **[Side Parameter & System Instruction 패널]** 2컬럼 레이아웃으로 전면 고도화합니다. 유저 질문과 LLM 대답이 개별 말풍선(Chat Bubble)으로 연속 렌더링되며, 실시간 SSE 토큰 글자 스트리밍 애니메이션과 하단 메트릭 칩(TTFT ms, Tok/s, Token Counts), cURL/SDK 코드 복사 바가 제공됩니다.

**Why this priority**: 최신 AI 개발자 도구(Google AI Studio, OpenAI Playground 3.0) 수준의 직관적이고 수려한 대화형 인퍼런스 샌드박스를 제공하여 사용자 만족도를 극대화합니다.

**Independent Test**:
1. AI Playground에서 질문 전송 시 메인 대화창에 User 말풍선 생성 후 Assistant 말풍선으로 SSE 스트리밍 답변이 글자 단위로 실시간 애니메이션 출력되는지 확인.
2. 하단 메트릭 칩(TTFT, Tok/s, Token Count) 및 cURL / Python 코드 복사 툴바가 정상 동작하는지 확인.

---

### User Story 2 - Audit 로그 대답 원문 Payload Inspector 팝업 모달 (Priority: P2)

웹 대시보드 "Audit & API Keys" 및 "Live Audit Log Timeline" 이력 테이블 행에서 **[👁️ View Payload (대답 보기)]** 버튼을 클릭하면, 입력 질문 프롬프트와 LLM 대답 생성 텍스트 원문을 한눈에 볼 수 있는 팝업 모달(`payload-modal`)을 표출합니다.

**Why this priority**: 과거 호출 이력에서 오답 원인 분석 및 모델 답변 검증을 신속히 수행합니다.

**Independent Test**: Audit 테이블 행의 "View Payload" 클릭 시 해당 요청의 프롬프트와 LLM 대답 텍스트가 팝업 창에 표출되는지 확인.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/core/metrics_db.py` SQLite DB schema에 `prompt_text` (TEXT) 및 `completion_text` (TEXT) 컬럼을 추가하고, `/v1/chat/completions` 요청 시 입력 프롬프트와 LLM 대답 텍스트를 저장해야 한다.
- **FR-002**: 웹 대시보드 Audit 로그 테이블(`src/api/static/index.html`)에 **[Payload View (대답 내용 보기)]** 버튼 열을 추가하고, 클릭 시 입력 질문과 LLM 대답 텍스트를 보여주는 모달(`payload-modal`)을 제공해야 한다.
- **FR-003**: `GET /dashboard/api/audit/payload/{request_id}` REST API 엔드포인트를 신설하여 특정 요청 ID의 LLM 대답 텍스트 및 상세 메트릭(TTFT, TPS, Tokens)을 반환해야 한다.
- **FR-004**: `config/server_config.json`에 `payload_logging_enabled` (기본값: true) 설정 옵션을 추가하여 데이터 저장 여부를 관리자가 온/오프할 수 있게 해야 한다.
- **FR-005**: AI Playground UI(`src/api/static/index.html` 및 `app.js`)를 Google AI Studio 2026 레퍼런스 기준 **2컬럼 레이아웃 [Chat Thread Main + Side Parameter Panel]**로 고도화해야 한다.
- **FR-006**: AI Playground 대화창에서 SSE (Server-Sent Events) 비동기 스트리밍 답변 글자 애니메이션 렌더링을 제공해야 한다.
- **FR-007**: AI Playground 하단에 **[TTFT ms, Tok/s, Token Counts, Est. Cost]** 실시간 메트릭 칩 및 cURL / Python SDK 코드 즉시 복사 바(Toolbar)를 통합 표출해야 한다.
- **FR-008**: Anti-Mock 헌법 v1.4.0에 따라 실제 LLM 대답 텍스트 저장 및 대시보드 Payload 조회 API 실측 테스트 수트(`tests/unit/test_llm_payload_viewer.py`)를 수록해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: Google AI Studio 2026 Style 대화형 Playground SSE 토큰 스트리밍 애니메이션 정상 표출률 **100%**.
- **SC-002**: 대시보드 Audit 탭에서 LLM 대답 내용 팝업 표출 정확도 **100%**.
- **SC-003**: Payload 조회 API (`GET /dashboard/api/audit/payload/{id}`) 응답 속도 **<15ms**.
- **SC-004**: `payload_logging_enabled: false` 시 프롬프트/대답 텍스트 미기록 보안 준수율 **100%**.

---

## Key Entities *(optional)*

- **Inference Payload Log Entity (`data/metrics.db`)**:
  ```sql
  ALTER TABLE api_key_logs ADD COLUMN prompt_text TEXT;
  ALTER TABLE api_key_logs ADD COLUMN completion_text TEXT;
  ```
