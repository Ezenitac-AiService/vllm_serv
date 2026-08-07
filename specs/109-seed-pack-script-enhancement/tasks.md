# Tasks: 시드 팩(Seed Pack) 생성 스크립트 최신 명세(GQA/GGUF/프로필) 반영 고도화 (Seed Pack Script Enhancement)

**Input**: Design documents from `/specs/109-seed-pack-script-enhancement/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly specified in task descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment verification and shell script setup

- [x] T001 Verify `scripts/make_seed_pack.sh` executable status and CLI option parser structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core verification helpers for archive inspection

- [x] T002 Add helper function `verify_archive_entry` to `scripts/make_seed_pack.sh` to validate mandatory files inside generated tarball/zip archive

---

## Phase 3: User Story 1 - GQA 파서 및 최신 아키텍처 수록 검증 (Priority: P1) 🎯 MVP

**Goal**: Feature 108의 `src/core/gpu_detector.py` (GQA VRAM 수식, GGUF 바이너리 헤더 파서) 및 `config/model_catalog.json`이 아카이브에 100% 필수 포함 및 수록 검증되도록 고도화.

**Independent Test**: `./make_seed_pack.sh` 구동 시 `src/core/gpu_detector.py` 및 `config/model_catalog.json` 수록 검증 메시지가 초록색(`✓`)으로 성공 출력되는지 실측 확인.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T003 [P] [US1] Create unit test for GQA GPU detector module & catalog inclusion (`test_seed_pack_includes_gpu_detector_and_catalog`) in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 1

- [x] T004 [US1] Update content verification section in `scripts/make_seed_pack.sh` to assert `src/core/gpu_detector.py` presence and log verification status
- [x] T005 [US1] Update content verification section in `scripts/make_seed_pack.sh` to assert `config/model_catalog.json` presence and log verification status

**Checkpoint**: User Story 1 is fully functional and testable independently (`./make_seed_pack.sh`).

---

## Phase 4: User Story 2 - 컨텍스트 프로필 동기화 및 선택적 포함 옵션 제공 (Priority: P2)

**Goal**: CLI 옵션 `--include-profiles` 지원을 통해 `config/model_context_profiles.json`을 선택적으로 아카이브에 포함하여 타겟 서버에서의 재탐색 시간을 단축.

**Independent Test**: `./make_seed_pack.sh --include-profiles` 구동 시 `config/model_context_profiles.json`이 압축 파일 내에 포함되는지 검증.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T006 [P] [US2] Create unit test verifying `--include-profiles` CLI flag (`test_seed_pack_include_profiles_flag`) in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 2

- [x] T007 [US2] Add `--include-profiles` flag handling to CLI option parser in `scripts/make_seed_pack.sh`
- [x] T008 [US2] Update exclude rules in `scripts/make_seed_pack.sh` to dynamically include `config/model_context_profiles.json` when `INCLUDE_PROFILES=1`
- [x] T009 [US2] Update help text and user migration guidelines in `scripts/make_seed_pack.sh` to document `--include-profiles`

**Checkpoint**: User Stories 1 AND 2 are both independently functional.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full test suite verification

- [x] T010 Run quickstart validation scenarios from `specs/109-seed-pack-script-enhancement/quickstart.md`
- [x] T011 Run complete test suite (`uv run pytest tests/unit/`) across all unit tests
- [x] T012 Verify Constitution Principle II & DoD compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion.
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion.
- **Polish (Phase 5)**: Depends on all user stories being complete.

---

## Implementation Strategy (MVP First)

1. **MVP Scope**: Complete Phase 1 ~ Phase 3 (User Story 1 - GQA parser & model catalog verification).
2. **Increment 2**: Add Phase 4 (User Story 2 - `--include-profiles` CLI flag).
3. **Final Polish**: Run `quickstart.md` scenarios and full `uv run pytest tests/unit/` test suite.
