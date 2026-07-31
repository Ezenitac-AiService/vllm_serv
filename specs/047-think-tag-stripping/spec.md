# Feature Specification: LLM 응답 내 <think> 추론 태그 자동 파싱 및 정제 (047-think-tag-stripping)

**Feature Branch**: `047-think-tag-stripping`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User feedback: "서 think 태그 어떻할꺼야, 지워진거야 만거야? 최대 출력 토큰 기본값이 왜 256이야? (LLM 응답 텍스트에 포함된 <think>...<think> 사고과정 태그 파싱 및 max_tokens 상향 필요)"

---

## Clarifications

### Session 2026-07-30

- Q: SSE 비동기 스트리밍(stream=True) 호출 시 <think> 추론 태그 처리 방식 → A: Option A (스트리밍 도중 <think>...</think> 태그 구간 토큰을 실시간 감지/필터링하여 클라이언트에 정제된 답변 토큰만 즉시 전송하고, 완료 후 DB에 추론 과정을 분리 기록)
- Q: LLM 응답 토큰 한계(max_tokens)로 인해 </think> 닫는 태그 없이 잘린 경우의 미완성 태그 처리 방식 → A: Option A (닫는 태그가 누락된 경우 전체를 thinking_process로 안전하게 격리하고, text에는 [Truncated during thinking process] 안내 메시지 반환)
- Q: AI Playground 및 API 요청 시 기본 최대 생성 토큰 수(max_tokens) 상향 설정 → A: Option A (max_tokens 기본값을 1024로 상향 설정하여 추론 과정 및 최종 답변이 잘리지 않고 완결되도록 보장)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - LLM 응답 내 `<think>...</think>` 추론 태그 자동 분리 및 정제 (Priority: P1) 🎯 MVP

AI Playground 및 `/v1/chat/completions` API를 통해 답변을 수신할 때, DeepSeek/Qwen 등 추론 모델이 생성하는 `<think>...</think>` 사고과정 태그 블록을 최종 사용자 응답 텍스트에서 깔끔하게 정제(Strip/Extract)하여 대답 본문에는 최종 답변만 깨끗하게 표출하고, 추론 과정은 `thinking_process` 전용 필드로 분리합니다.

**Why this priority**: 사용자 프롬프트에 대한 최종 대답 텍스트에 태그 기호와 내부 사유 과정이 섞여 출력되면 시각적 노이즈가 발생하고 가독성이 크게 저하됩니다.

**Independent Test**:
1. AI Playground에서 추론 모델로 질문 전송 시 `<think>사고과정...</think>최종 답변입니다.` 구조의 응답에서 `<think>` 태그 및 내부 사고과정이 정제되고 `text` 필드에는 "최종 답변입니다."만 정상 출력되는지 확인.

---

### User Story 2 - Playground 및 Audit Payload 뷰어 추론 과정 접기/펼치기 UI (Priority: P2)

AI Playground 대화 스레드 및 대시보드 Audit 탭의 [👁️ View Payload] 팝업 모달에서 정제된 최종 답변과 함께 파싱된 추론 과정(`thinking_process`)을 별도의 접이식 아코디언("🧠 Thinking Process")으로 분리하여 표출합니다.

**Why this priority**: 디버깅이나 성능 평가 시 LLM이 어떤 논리적 과정을 거쳐 답변을 도출했는지 원문을 확인할 수 있어야 합니다.

**Independent Test**:
1. Audit Payload 뷰어 팝업 모달 열기 시 최종 대답과 추론 과정(Thinking Trace)이 독립된 영역으로 구분되어 표출되는지 확인.

---

### User Story 3 - `<think>` 태그 정제 동작 제어 옵션 (`strip_think_tags`) (Priority: P3)

요청 파라미터 또는 시스템 설정(`strip_think_tags: true/false`)을 통해 클라이언트가 필요 시 원문 그대로 `<think>` 태그를 포함하여 수신할지, 자동 정제된 텍스트를 수신할지 동적으로 제어할 수 있습니다.

**Why this priority**: 원문 텍스트 전체를 직접 파싱하려는 외부 에이전트 마이크로서비스 및 개발자 클라이언트를 위한 호환성을 제공합니다.

**Independent Test**:
1. `strip_think_tags=false` 파라미터 전달 시 원문 `<think>` 태그가 포함된 전체 텍스트가 반환되는지 확인.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/api/routes/dashboard_api.py` 및 `src/api/routes/inference_api.py`에서 백엔드 LLM 생성 응답 텍스트 내 `<think>...</think>` 태그 블록을 원자적으로 파싱 및 추출/제거해야 한다.
- **FR-002**: `POST /dashboard/api/playground` 응답의 `text` 필드에는 정제된 최종 대답만 리턴하고, 파싱된 추론 과정은 `thinking_process` 필드에 분리 수록해야 한다.
- **FR-003**: `data/metrics.db` 로깅 시 정제된 `completion_text`와 함께 파싱된 `thinking_text`를 안전하게 기록해야 한다.
- **FR-004**: Anti-Mock 헌법 v1.5.2에 따라 `<think>` 태그 파싱, 분리 및 렌더링 실측 검증 테스트 수트(`tests/unit/test_think_tag_stripping.py`)를 수록해야 한다.
- **FR-005**: SSE 비동기 스트리밍(`stream=True`) 처리 시 `<think>...</think>` 구간 토큰을 실시간 감지/필터링하여 클라이언트 스트림에는 정제된 답변 토큰만 즉시 전송하고, 완료 후 `thinking_process`와 함께 `metrics_db`에 원자적 수록해야 한다.
- **FR-006**: 토큰 한계 등으로 `</think>` 닫는 태그 없이 응답이 잘린 경우, `<think>` 이후 수신된 모든 텍스트를 `thinking_process`로 격리하고 `text` 필드에는 `[Truncated during thinking process]` 안내 메시지를 반환하여 오염을 방지해야 한다.
- **FR-007**: AI Playground (`POST /dashboard/api/playground`) 및 API 기본 `max_tokens` 설정을 기존 256에서 `1024`로 상향 조정하여 `<think>` 추론 과정과 최종 답변 생성 완결성을 보장해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: AI Playground 및 인퍼런스 API 응답에서 `<think>` 태그 노출 없는 정제 대답 표출 성공률 **100%**.
- **SC-002**: `<think>` 블록 파싱 및 `thinking_process` 분리 정확도 **100%**.
- **SC-003**: `<think>` 태그 파싱 및 정제 처리 추가 오버헤드 지연시간 **<1ms**.

---

## Key Entities *(optional)*

- **Playground Response Object (`src/api/routes/dashboard_api.py`)**:
  ```json
  {
    "text": "대한민국의 수도는 서울입니다.",
    "thinking_process": "사용자가 한국의 수도를 물었으므로 수도에 대한 factual data 조회...",
    "ttft_ms": 42.1,
    "total_latency_s": 0.85,
    "token_speed_tok_s": 32.5,
    "prompt_tokens": 12,
    "completion_tokens": 40,
    "finish_reason": "stop"
  }
  ```
