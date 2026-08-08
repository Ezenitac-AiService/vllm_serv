# Tasks: Qwen 3.5 9B 멀티모달 모델 검증 및 별도 카탈로그 등록 (qwen35-multimodal-model)

**Input**: Design documents from `/specs/119-qwen35-multimodal-model/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are mandatory per Constitution Principles II, IV, and VII.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project configuration structure and environment setup

- [x] T001 Inspect `config/model_catalog.json` and prepare catalog schema verification structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core test infrastructure for model catalog validation that MUST be complete before user story implementation

- [x] T002 [P] Create catalog test suite for Qwen 3.5 9B multimodal in `tests/unit/test_qwen35_multimodal_catalog.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Qwen 3.5 9B 멀티모달 별도 카탈로그 항목(`qwen3.5-9b-vision`) 추가 (Priority: P1) 🎯 MVP

**Goal**: 기존 `qwen3.5-9b` 텍스트 전용 카탈로그 항목의 하위 호환성을 유지하면서, 비전 프로젝터(`mmproj-BF16.gguf`)가 추가된 `qwen3.5-9b-vision` 신규 엔트리를 `config/model_catalog.json`에 추가한다.

**Independent Test**: `uv run pytest tests/unit/test_qwen35_multimodal_catalog.py` 실행 시 `qwen3.5-9b` (텍스트)와 `qwen3.5-9b-vision` (멀티모달) 두 항목의 보존 및 올바른 생성을 실측 단정한다.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T003 [P] [US1] Write test assertions for `qwen3.5-9b-vision` catalog entry and `qwen3.5-9b` text-only preservation in `tests/unit/test_qwen35_multimodal_catalog.py`

### Implementation for User Story 1

- [x] T004 [P] [US1] Add `qwen3.5-9b-vision` entry to `config/model_catalog.json` with `requires_mmproj: true`, `clip_filename: "mmproj-BF16.gguf"`, and `clip_path: "models/qwen3.5-9b-vision/mmproj-BF16.gguf"`
- [x] T005 [US1] Run unit test in `tests/unit/test_qwen35_multimodal_catalog.py` to confirm catalog integrity and pass green

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and independently verified.

---

## Phase 4: User Story 2 - 신규 멀티모달 모델(`qwen3.5-9b-vision`) 구동 및 서버 설정 연동 (Priority: P2)

**Goal**: `qwen3.5-9b-vision` 카탈로그 항목이 모델 동기화 스크립트(`scripts/ensure_models.py`) 및 서버 구동 스크립트(`scripts/start_server.sh`)의 `--mmproj` 비전 프로젝터 옵션 바인딩과 정상 연동되는지 검증한다.

**Independent Test**: `uv run pytest tests/integration/test_multimodal_server_config.py` 실행으로 `qwen3.5-9b-vision` 모델 선택 시 `--mmproj` 파라미터 파싱 및 파일 존재 감지를 통합 검증한다.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T006 [P] [US2] Create integration test for multimodal model download and server CLI options in `tests/integration/test_multimodal_server_config.py`

### Implementation for User Story 2

- [x] T007 [US2] Update and verify `scripts/ensure_models.py` to handle both main GGUF and `mmproj` files for `qwen3.5-9b-vision`
- [x] T008 [US2] Verify `scripts/start_server.sh` CLI option construction for `qwen3.5-9b-vision` with `--mmproj` flag
- [x] T009 [US2] Run integration test in `tests/integration/test_multimodal_server_config.py` and pass green

**Checkpoint**: Both User Story 1 and User Story 2 are independently functional and integrated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing and documentation updates

- [x] T010 [P] Update documentation in `README.md` to reference `qwen3.5-9b-vision` multimodal model support
- [x] T011 Run quickstart validation script from `specs/119-qwen35-multimodal-model/quickstart.md`
- [x] T012 Execute full regression test suite with `uv run pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion and Phase 3 catalog entry
- **Polish (Phase 5)**: Depends on User Stories completion

### Parallel Opportunities

- T002 (Foundational test creation) can run in parallel
- T003 & T004 (US1 test & catalog json entry) can run in parallel
- T006 & T010 (US2 test & README update) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2
2. Complete Phase 3 (US1 - `config/model_catalog.json` update + unit tests)
3. Run `uv run pytest tests/unit/test_qwen35_multimodal_catalog.py`
4. Validate MVP delivery

### Full Delivery

1. Complete MVP (US1)
2. Complete Phase 4 (US2 - script integration & `--mmproj` binding)
3. Execute Phase 5 full regression suite (`uv run pytest`)
