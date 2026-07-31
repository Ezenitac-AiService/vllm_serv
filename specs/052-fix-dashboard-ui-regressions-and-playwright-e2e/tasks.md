# Tasks: 대시보드 UI 회귀 버그 원인 분석, 근본 수리 및 Playwright E2E 테스트 수트 구축 (052-fix-dashboard-ui-regressions-and-playwright-e2e)

**Input**: `/specs/052-fix-dashboard-ui-regressions-and-playwright-e2e/` 디자인 문서 (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

---

## Phase 1: Setup (공통 기반 작업)

**목적**: Playwright 패키지 추가 및 Chromium Headless 브라우저 설치

- [X] T001 [P] `uv add pytest-playwright` 패키지 설치 및 `uv run playwright install chromium` 헤드리스 브라우저 드라이버 환경 구축

---

## Phase 2: Foundational (선행 블로킹 전제조건)

**목적**: `app.js` 내 누락된 `modalCloseBtn` 복원 및 Optional Chaining 전면 적용

- [X] T002 `src/api/static/app.js`의 `elements` 객체에 누락된 `modalCloseBtn: document.getElementById('modal-close-btn')` 복원 및 이벤트 바인딩 가드 처리

---

## Phase 3: User Story 1 - UI 회귀 버그 근본 수리 및 방어 프로그래밍 (Priority: P1) 🎯 MVP

**목적**: 관리자 인증 모달, Form 제출 새로고침 차단 및 뷰 버튼 이벤트 핸들링 정상화

**독립 테스트**: 관리자 모달 (로그인/취소 버튼) 동작 확인 및 Form 제출 시 탭 리셋 현상 차단 확인

### User Story 1 구현

- [X] T003 [US1] `src/api/static/app.js`의 `manualForm` 제출 리스너 첫 줄에 `e.preventDefault()`를 필수 구동하여 Form 제출 시 브라우저 새로고침 및 탭 리셋 현상 차단
- [X] T004 [US1] `src/api/static/app.js` 내 모든 버튼(`adminLoginBtn`, `modalLoginBtn`, `modalCloseBtn`, `unloadBtn`, `codeExportBtn`, `refreshAuditBtn` 등) 리스너에 Optional Chaining(`?.`) 적용 및 동작 수리

---

## Phase 4: User Story 2 - Playwright E2E 자동화 회귀 테스트 수트 구축 (Priority: P1) 🎯 MVP

**목적**: 실제 Headless 브라우저 환경에서 전체 탭, 모달, 폼, 버튼을 실체적으로 검증하는 E2E 수트 구축

**독립 테스트**: `uv run pytest tests/e2e/test_dashboard_ui.py -v` 100% 그린 패스

### User Story 2 구현 & 테스트

- [X] T005 [P] [US2] `tests/e2e/test_dashboard_ui.py`에 Playwright 기반 대시보드 4개 탭 전환, 관리자 모달(로그인/취소), Form 제출 새로고침 방지 E2E 테스트 수트 작성
- [X] T006 [US2] `uv run pytest tests/e2e/test_dashboard_ui.py -v` 명령으로 Playwright E2E 브라우저 실측 검증 수행

---

## Phase 5: Polish & Cross-Cutting Concerns (다듬기 및 마무리)

**목적**: 전체 회귀 테스트 검증 및 문서 업데이트

- [X] T007 [P] `uv run pytest tests/unit/test_model_select_display_fix.py tests/unit/test_playground_api_key_auth.py tests/unit/test_playground_model_selection.py tests/unit/test_think_tag_ui_markdown.py tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py tests/e2e/test_dashboard_ui.py -v` 전체 회귀 검증 수행 (헌법 v1.6.0 원칙 VII)
- [X] T008 [P] `specs/052-fix-dashboard-ui-regressions-and-playwright-e2e/quickstart.md`에 E2E 및 회귀 검증 결과 기록 갱신

---

## Dependencies & Execution Order (의존성 및 실행 순서)

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 완료됨
- **Foundational (Phase 2)**: Phase 1 완료 후 완료됨
- **User Stories (Phase 3 & 4)**: Phase 1 & 2 완료 후 완료됨
- **Polish (Phase 5)**: 사용자 스토리 완료 후 완료됨

---

## Implementation Strategy (구현 전략)

### MVP First (User Story 1 & 2)

1. Phase 1 & 2: Setup & Foundational 완료 (`playwright` 추가 및 `app.js` `modalCloseBtn` 복원)
2. Phase 3 & 4: UI 버그 수리 및 Playwright E2E 수트 작성
3. 독립 검증: `uv run pytest tests/e2e/test_dashboard_ui.py -v` 완료 (22/22 tests passed)
