# Tasks: 멀티모달(비전) 모델 로딩 및 이미지 입력 서빙 검증 (verify-multimodal-image-serving)

**Input**: Design documents from `/specs/120-verify-multimodal-image-serving/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are mandatory per Constitution Principles II, IV, and VII.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify multimodal model catalog configuration structure and 32GB RAM / 11GB VRAM hardware tier settings

- [x] T001 Inspect `config/model_catalog.json` and verify `requires_mmproj` and `clip_path` for `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, and `qwen3.5-9b-vision`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core test infrastructure for multimodal CLI binding and API proxy validation that MUST be complete before user story implementation

- [x] T002 [P] Create unit test suite for multimodal CLI binding in `tests/unit/test_process_manager_multimodal.py`
- [x] T003 [P] Create integration test suite for OpenAI image payload proxy in `tests/integration/test_multimodal_image_payload_proxy.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Gemma 4 및 Qwen 3.5 9B Vision 멀티모달 모델 바인딩 및 11GB VRAM 구동 검증 (Priority: P1) 🎯 MVP

**Goal**: 멀티모달 모델 4종(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-9b-vision`) 스폰 시 `ProcessManager`가 `--mmproj <clip_path>` CLI 옵션을 올바르게 추가하고 11GB VRAM 한계 및 프로젝터 미존재 시 에러를 검증한다.

**Independent Test**: `uv run pytest tests/unit/test_process_manager_multimodal.py` 실행 시 4개 모델 전체의 `--mmproj` 인자 결합 및 에러 핸들링을 실측 단정한다.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T004 [P] [US1] Write test cases asserting `--mmproj` CLI argument injection for `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, and `qwen3.5-9b-vision` in `tests/unit/test_process_manager_multimodal.py`
- [x] T005 [P] [US1] Write test cases asserting missing `clip_path` error handling and 11GB VRAM estimation checks for multimodal models in `tests/unit/test_process_manager_multimodal.py`

### Implementation for User Story 1

- [x] T006 [US1] Update and verify `src/core/process_manager.py` to ensure `--mmproj` CLI parameter is correctly built for all 4 multimodal models
- [x] T007 [US1] Run unit tests in `tests/unit/test_process_manager_multimodal.py` to confirm CLI binding integrity and pass green

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and independently verified.

---

## Phase 4: User Story 2 - OpenAI 호환 이미지 입력 Payload (`image_url` / Base64) 및 25MB 크기 제한 라우팅 검증 (Priority: P2)

**Goal**: OpenAI 규격의 이미지 요청 페이로드(`image_url` 내 Data URL Base64 및 HTTP URL)가 25MB 크기 제한 내에서 역방향 프록시(`src/api/routes/inference_api.py`)를 통해 백엔드로 손상 없이 전달되고, 25MB 초과 페이로드에 대해 HTTP 413 에러를 반환함을 검증한다.

**Independent Test**: `uv run pytest tests/integration/test_multimodal_image_payload_proxy.py` 실행으로 멀티모달 이미지 페이로드 라우팅 및 25MB 제한 413 방어를 통합 검증한다.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T008 [P] [US2] Write integration test for Data URL Base64 image payload routing in `tests/integration/test_multimodal_image_payload_proxy.py`
- [x] T009 [P] [US2] Write integration test for HTTP image URL payload routing in `tests/integration/test_multimodal_image_payload_proxy.py`
- [x] T010 [P] [US2] Write integration test for 25MB HTTP payload body size limit enforcement (HTTP 413 Payload Too Large) in `tests/integration/test_multimodal_image_payload_proxy.py`

### Implementation for User Story 2

- [x] T011 [US2] Verify reverse proxy payload forwarding and 25MB body limit validation logic in `src/api/routes/inference_api.py` for multimodal chat completion requests
- [x] T012 [US2] Run integration tests in `tests/integration/test_multimodal_image_payload_proxy.py` and pass green

**Checkpoint**: Both User Story 1 and User Story 2 are independently functional and integrated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing and documentation updates

- [x] T013 [P] Update documentation in `README.md` to reference multimodal image payload support and 25MB request size limit
- [x] T014 Run quickstart validation script from `specs/120-verify-multimodal-image-serving/quickstart.md`
- [x] T015 Execute full regression test suite with `uv run pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion and Phase 3 CLI binding
- **Polish (Phase 5)**: Depends on User Stories completion

### Parallel Opportunities

- T002 & T003 (Foundational unit and integration test creation) can run in parallel
- T004 & T005 & T008 & T009 & T010 (Test writing tasks) can run in parallel
- T013 (README update) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2
2. Complete Phase 3 (US1 - `--mmproj` CLI binding verification + unit tests)
3. Run `uv run pytest tests/unit/test_process_manager_multimodal.py`
4. Validate MVP delivery

### Full Delivery

1. Complete MVP (US1)
2. Complete Phase 4 (US2 - OpenAI image payload reverse proxy routing, 25MB limit & integration tests)
3. Execute Phase 5 full regression suite (`uv run pytest`)
