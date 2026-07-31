# Tasks: API Key 필수 모드 시 Playground 인증 처리 및 API Key 입력 지원 (050-playground-api-key-auth)

**Input**: `/specs/050-playground-api-key-auth/` 디자인 문서 (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

---

## Phase 1: Setup (공통 기반 작업)

**목적**: Playground 설정 패널 UI API Key 입력 요소 추가

- [X] T001 [P] `src/api/static/index.html` Playground 설정 패널에 API Key 입력 UI (`<input id="pg-api-key">`) 추가

---

## Phase 2: Foundational (선행 블로킹 전제조건)

**목적**: 백엔드 capabilities API의 `api_key_enabled` 보안 상태 반환 구현

- [X] T002 `src/api/routes/dashboard_api.py`의 `GET /dashboard/api/capabilities` 응답에 `api_key_enabled: bool` 상태값 추가

---

## Phase 3: User Story 1 - API Key 필수 모드(`api_key_enabled`) 활성화 시 Playground 인증 처리 (Priority: P1) 🎯 MVP

**목적**: 보안 모드 활성화 시 Playground 호출에 유효한 API Key 검증을 적용하고 미제공 시 401 차단 및 에러 안내

**독립 테스트**: 보안 모드 ON 설정 후 API Key 미제공 시 401 차단 및 유효한 API Key 전송 시 정상 추론 스트리밍 성공 검증

### User Story 1 테스트

- [X] T003 [P] [US1] `tests/unit/test_playground_api_key_auth.py`에 API Key 필수 모드 ON/OFF 시 401 차단 및 정상 인증 검증 단위 테스트 작성

### User Story 1 구현

- [X] T004 [US1] `src/api/routes/dashboard_api.py`의 `PlaygroundRequest`에 `api_key` 필드 추가 및 `run_playground_stream` / `run_playground_test`에서 `api_key_enabled` ON 시 API Key 검증 및 401 Unauthorized 반환 구현
- [X] T005 [US1] `src/api/static/app.js`에서 capabilities의 `api_key_enabled` 수신 후 UI 플레이스홀더 갱신, 추론 요청 시 `#pg-api-key` 전달 및 401 수신 시 경고 알림 표시 구현

---

## Phase 4: Polish & Cross-Cutting Concerns (다듬기 및 마무리)

**목적**: 전체 회귀 테스트 검증 및 문서 업데이트

- [X] T006 [P] `uv run pytest tests/unit/test_playground_api_key_auth.py tests/unit/test_playground_model_selection.py tests/unit/test_think_tag_ui_markdown.py tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py -v` 전체 회귀 검증 수행
- [X] T007 [P] `specs/050-playground-api-key-auth/quickstart.md`에 최종 테스트 결과 및 UI 검증 기록 갱신

---

## Dependencies & Execution Order (의존성 및 실행 순서)

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 완료됨
- **Foundational (Phase 2)**: Phase 1 완료 후 완료됨
- **User Stories (Phase 3)**: Phase 1 & 2 완료 후 완료됨
- **Polish (Phase 4)**: 사용자 스토리 완료 후 완료됨

---

## Implementation Strategy (구현 전략)

### MVP First (User Story 1)

1. Phase 1 & 2: Setup & Foundational 완료 (UI 필드 및 capabilities 상태 전달)
2. Phase 3: User Story 1 구현 (401 차단 및 frontend API Key 전달)
3. 독립 검증: `uv run pytest tests/unit/test_playground_api_key_auth.py` 완료 (16/16 tests passed)
