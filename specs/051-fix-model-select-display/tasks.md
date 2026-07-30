# Tasks: 대시보드 및 플레이그라운드 동적 서비스 모델 선택 드롭다운 목록 미표시 근본 원인 버그 수정 (051-fix-model-select-display)

**Input**: `/specs/051-fix-model-select-display/` 디자인 문서 (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

---

## Phase 1: Setup (공통 기반 작업)

**목적**: `config/model_catalog.json` 카탈로그 구조 확인 및 로더 기초 검증

- [X] T001 [P] `config/model_catalog.json` 항목 구조 확인 및 동적 카탈로그 키 로드 설정 검증

---

## Phase 2: Foundational (선행 블로킹 전제조건)

**목적**: `ConfigManager` 캐시 고착 결함 수리

- [X] T002 `src/core/config_manager.py`의 `get_model_catalog()`에서 `_model_catalog_cache` 캐시가 빈 딕셔너리(`{}`)로 고착되지 않도록 로더 예외 처리 수리

---

## Phase 3: User Story 1 - 동적 모델 카탈로그 로드 및 드롭다운 연동 근본 수리 (Priority: P1) 🎯 MVP

**목적**: 백엔드 동적 카탈로그 반환 수리 및 대시보드/플레이그라운드 드롭다운 완벽 바인딩

**독립 테스트**: `ConfigManager` 반복 호출 시 동적 카탈로그 로드 검증 및 `GET /dashboard/api/capabilities` 응답을 통한 드롭다운 바인딩 성공 검증

### User Story 1 테스트

- [X] T003 [P] [US1] `tests/unit/test_model_select_display_fix.py`에 `ConfigManager.get_model_catalog()` 캐시 비오염 및 capabilities API 동적 모델 응답 단위 테스트 작성

### User Story 1 구현

- [X] T004 [US1] `src/api/routes/dashboard_api.py`의 `get_capabilities` 함수에서 동적 카탈로그 모델 키를 `available_models`로 정확히 전달하도록 수리
- [X] T005 [US1] `src/api/static/app.js`의 `loadCapabilities()`에서 수신된 `available_models` 크기에 맞추어 `#model-select` 및 `#pg-model-select` 드롭다운 옵션을 동적으로 완전 바인딩하도록 구현

---

## Phase 4: Polish & Cross-Cutting Concerns (다듬기 및 마무리)

**목적**: 전체 회귀 테스트 검증 및 문서 업데이트

- [X] T006 [P] `uv run pytest tests/unit/test_model_select_display_fix.py tests/unit/test_playground_api_key_auth.py tests/unit/test_playground_model_selection.py tests/unit/test_think_tag_ui_markdown.py tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py -v` 전체 회귀 검증 수행
- [X] T007 [P] `specs/051-fix-model-select-display/quickstart.md`에 최종 테스트 결과 및 UI 검증 기록 갱신

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

1. Phase 1 & 2: Setup & Foundational 완료 (`ConfigManager` 캐시 고착 버그 수정)
2. Phase 3: User Story 1 구현 (백엔드 API 및 frontend 드롭다운 동적 바인딩)
3. 독립 검증: `uv run pytest tests/unit/test_model_select_display_fix.py` 완료 (18/18 tests passed)
