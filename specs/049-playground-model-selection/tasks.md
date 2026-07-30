# Tasks: AI Playground 동적 모델 선택 및 서버 온로드 모델 자동 동기화 (049-playground-model-selection)

**Input**: `/specs/049-playground-model-selection/` 디자인 문서 (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

---

## Phase 1: Setup (공통 기반 작업)

**목적**: Playground 설정 패널 UI 드롭다운 요소 추가

- [X] T001 [P] `src/api/static/index.html` Playground 설정 패널에 모델 선택 드롭다운 UI (`<select id="pg-model-select">`) 추가

---

## Phase 2: Foundational (선행 블로킹 전제조건)

**목적**: 백엔드 REST API의 모델 파라미터 바인딩 검증

- [X] T002 `src/api/routes/dashboard_api.py`의 `PlaygroundRequest` 및 `run_playground_stream` 메서드가 동적 `model` 인자를 정상 수신하도록 검증

---

## Phase 3: User Story 1 - 서버 온로드 모델 자동 기본 선택 및 Playground 드롭다운 전환 (Priority: P1) 🎯 MVP

**목적**: 대시보드 로딩 시 현재 서버 온로드 모델(`current_model`)을 기본값으로 자동 설정하고 드롭다운 변경 후 질문 전송 시 선택 모델 반영

**독립 테스트**: 대시보드 진입 시 드롭다운 기본값이 온로드 모델로 지정되고 선택 전환 후 전송 시 해당 모델 파라미터가 적용되는지 검증

### User Story 1 테스트

- [X] T003 [P] [US1] `tests/unit/test_playground_model_selection.py`에 capabilities 조회 및 동적 모델 파라미터 전달 단위 테스트 작성

### User Story 1 구현

- [X] T004 [US1] `src/api/static/app.js`에서 `GET /dashboard/api/capabilities` 수신 시 `#pg-model-select` 옵션 동적 생성 및 `current_model` 자동 선택 설정, 모델 온로드/언로드 시 자동 갱신
- [X] T005 [US1] `src/api/static/app.js`의 `POST /dashboard/api/playground/stream` 추론 요청 시 `#pg-model-select` 선택값을 `model` 페이로드로 전송

---

## Phase 4: User Story 2 - 실시간 추론 지표 표출 (TTFT, TPS, Latency, Tokens) (Priority: P1)

**목적**: SSE 이벤트 파싱 오류(`JSON.parse`) 교정으로 TTFT(ms), Latency(s), Token Count 실시간 지표 복구

**독립 테스트**: 추론 스트리밍 완료 후 화면 카드에 TTFT, 총 소요시간, 토큰 카운트가 정상 표출되는지 검증

### User Story 2 구현

- [X] T006 [US2] `src/api/static/app.js`의 SSE `metrics` 이벤트 파싱 로직(`JSON.parse`)을 올바르게 교정하여 TTFT, Latency, Token Count 지표를 실시간 표시

---

## Phase 5: Polish & Cross-Cutting Concerns (다듬기 및 마무리)

**목적**: 전체 회귀 테스트 검증 및 문서 업데이트

- [X] T007 [P] `uv run pytest tests/unit/test_playground_model_selection.py tests/unit/test_think_tag_ui_markdown.py tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py -v` 전체 회귀 검증 수행
- [X] T008 [P] `specs/049-playground-model-selection/quickstart.md`에 최종 테스트 결과 및 UI 검증 기록 갱신

---

## Dependencies & Execution Order (의존성 및 실행 순서)

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 완료됨
- **Foundational (Phase 2)**: Phase 1 완료 후 완료됨
- **User Stories (Phase 3 & 4)**: Phase 1 & 2 완료 후 완료됨
- **Polish (Phase 5)**: 모든 사용자 스토리 완료 후 완료됨

---

## Implementation Strategy (구현 전략)

### MVP First (User Story 1 & 2)

1. Phase 1 & 2: Setup & Foundational 완료 (UI 드롭다운 및 백엔드 파라미터 검증)
2. Phase 3: User Story 1 구현 (온로드 모델 자동 동기화 및 드롭다운 선택 전송)
3. Phase 4: User Story 2 구현 (SSE `JSON.parse` 교정 및 지표 표출)
4. 독립 검증: `uv run pytest tests/unit/test_playground_model_selection.py` 완료 (14/14 tests passed)
