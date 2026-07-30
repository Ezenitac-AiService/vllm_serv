# Feature Specification: 실시간 LLM 백엔드 엔진 연동 Playground & 프롬프트/응답 원문 Payload 캡처 고도화 (046-real-llm-playground-payload)

**Feature Branch**: `046-real-llm-playground-payload`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User feedback: "아니, 답변 내용이 이게 뭐야, 처음에는 llm의 답변이 표시가 안되고 정보를 찍은 줄 알았는데, 개선된 내용 보니 그게 아니네? 사용자 질문이 전달이 안되는거야? 답변을 안받아오는거야? (플레이그라운드가 더미 샘플 텍스트 대신 실제 백엔드 llama-server C++ 엔진으로 사용자 프롬프트를 전송하고 실제 LLM 모델이 생성한 생생한 답변 텍스트를 수신 및 Audit DB에 원자적 저장)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Playground 실제 백엔드 LLM 모델 인퍼런스 연동 (Priority: P1) 🎯 MVP

AI Playground에서 사용자가 입력한 질문과 시스템 프롬프트가 더미 텍스트를 반환하는 대신, 현재 VRAM 상주 구동 중인 백엔드 C++ LLM 엔진(`llama-server` / `/v1/chat/completions`)으로 직접 전달되고, 모델이 실시간 생성한 **진짜 답변 텍스트(Real LLM Completion Output)**를 받아와 대화 챗 스레드 및 메트릭(TTFT, Tok/s)에 정확히 렌더링합니다.

**Why this priority**: 더미 시뮬레이션 응답이 아닌 실제 가동 중인 Qwen/Gemma 모델의 지능 응답을 플레이그라운드에서 직접 검증할 수 있어야 합니다.

**Independent Test**:
1. AI Playground에서 "한국의 수도는 어디인가요?" 입력 시 백엔드 C++ `llama-server` 인퍼런스를 거쳐 "대한민국의 수도는 서울입니다."와 같은 실제 LLM 생성 답변이 정상 출력되는지 확인.

---

### User Story 2 - `/v1/*` 역방향 프록시 및 Playground 실제 Payload 캡처 (Priority: P2)

클라이언트가 `/v1/chat/completions` API를 직접 호출하거나 Playground를 사용할 때, 사용자 질문(Prompt)과 LLM 생성 대답(Completion Text)의 실제 텍스트 원문을 캡처하여 SQLite `data/metrics.db`의 `prompt_text` 및 `completion_text` 컬럼에 100% 정밀 저장합니다.

**Why this priority**: 대시보드 Audit 탭의 **[👁️ View Payload (대답 보기)]** 팝업 모달 클릭 시 실제 질문과 실제 모델 생성 답변 원문이 정확히 표출되어야 오답 원인 분석 및 보안 감사가 완료됩니다.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `POST /dashboard/api/playground` 엔드포인트를 고도화하여 더미 텍스트 생성을 제거하고 `src/api/routes/inference_api.py` 내부 `_default_client`를 통해 백엔드 `llama-server` 엔진(`http://127.0.0.1:8089/v1/chat/completions`)으로 실제 HTTP 비동기 요청을 전송 및 실제 LLM 대답 텍스트를 수신해야 한다.
- **FR-002**: 백엔드 C++ `llama-server` 미구동 상태(`check_llama_status() == False`)인 경우 플레이그라운드에 "Model loading or offline" 가이드 및 fallback 안내 메시지를 명확히 리턴해야 한다.
- **FR-003**: `src/api/routes/inference_api.py`의 `reverse_proxy` 및 `playground` 핸들러에서 실제 Request Body의 `messages`/`prompt` 텍스트와 Response Body의 `choices[0].message.content` 생성 대답 텍스트를 파싱하여 `metrics_db.log_request`에 원자적 기록해야 한다.
- **FR-004**: Anti-Mock 헌법 v1.4.0에 따라 실제 `llama-server` 인퍼런스 프록시 통신 및 Payload 원문 저장/조회 실측 테스트 수트(`tests/unit/test_real_llm_playground_payload.py`)를 수록해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: AI Playground 실제 LLM 생성 대답 수신 및 표출 성공률 **100%**.
- **SC-002**: `/v1/chat/completions` 인퍼런스 요청 시 SQLite DB `prompt_text` 및 `completion_text` 실측 원문 저장 정확도 **100%**.
- **SC-003**: 백엔드 `llama-server` 실시간 역방향 프록시 지연 오버헤드 **<5ms**.

---

## Key Entities *(optional)*

- **Playground Real Request Payload (`src/api/routes/dashboard_api.py`)**:
  ```json
  {
    "model": "qwen3.5-4b",
    "messages": [
      {"role": "system", "content": "You are a helpful AI assistant."},
      {"role": "user", "content": "Actual user prompt..."}
    ],
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 256
  }
  ```
