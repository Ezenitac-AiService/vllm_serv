# Tasks: Seed Pack 복원 스크립트 고도화 (Unpack Seed Script Enhancement)

**Input**: Design documents from `/specs/111-unpack-seed-script-enhancement/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly specified in task descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify current `scripts/unpack_seed.sh` entrypoint and CLI options structure

- [x] T001 Verify current `scripts/unpack_seed.sh` entrypoint and basic execution flow

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core archive format detection helper for `.tar.gz` and `.zip`

- [x] T002 Implement archive type detection helper (`detect_archive_type`) in `scripts/unpack_seed.sh` supporting `.tar.gz` and `.zip` header/extension analysis

---

## Phase 3: User Story 1 - 멀티 포맷(.tar.gz & .zip) 동적 자동 감지 및 비파괴형(-k/-n) 복원 (Priority: P1) 🎯 MVP

**Goal**: `unpack_seed.sh`가 `.tar.gz` 및 `.zip` 아카이브 포맷을 동적 자동 감지하고, 기존 검증 통과 휠 바이너리를 덮어쓰지 않고 안전하게 비파괴 복원(`tar -xvkpf` / `unzip -n -q`)하도록 구현.

**Independent Test**: `./scripts/unpack_seed.sh dist/vllm_serv_seed.zip` 및 `./scripts/unpack_seed.sh dist/vllm_serv_seed.tar.gz` 실행 시 각각의 포맷을 인식하고 기존 유효 바이너리를 보존하며 압축 해제 완결.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T003 [P] [US1] Create unit tests for `.tar.gz` and `.zip` archive auto-detection and non-destructive extraction (`test_unpack_seed_multiformat_and_nondestructive`) in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 1

- [x] T004 [US1] Implement non-destructive extraction execution (`tar -xvkpf` for tarball and `unzip -n -q` for zip) in `scripts/unpack_seed.sh`
- [x] T005 [US1] Implement existing wheel binary preservation check (`verify_wheel_binary.py --check-live`) in `scripts/unpack_seed.sh`

**Checkpoint**: User Story 1 is fully functional and testable independently (`./scripts/unpack_seed.sh [archive_file]`).

---

## Phase 4: User Story 2 - CLI 입력 옵션 체계화 및 사전 무결성 검증 (Priority: P2)

**Goal**: 표준 CLI 플래그 (`-i`/`--input`, `-t`/`--target-dir`, `-f`/`--force-overwrite`, `--verify-only`, `-h`/`--help`) 및 압축 해제 전 필수 구성 요소 사전 무결성 검증 구현.

**Independent Test**: `./scripts/unpack_seed.sh -i custom.zip -t /tmp/dest --verify-only` 실행 시 압축 해제 없이 사전 무결성 검증만 정확히 수행됨을 확인.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T006 [P] [US2] Create unit tests for CLI argument parsing (`-i`, `-t`, `-f`, `--verify-only`) and pre-unpack verification in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 2

- [x] T007 [US2] Implement CLI argument parser loop (`while [[ $# -gt 0 ]]`) in `scripts/unpack_seed.sh`
- [x] T008 [US2] Implement pre-unpack archive integrity verification (`verify_archive_integrity`) for required entries in `scripts/unpack_seed.sh`

**Checkpoint**: User Stories 1 AND 2 are both independently functional.

---

## Phase 5: User Story 3 - 사후 무결성 검증 및 원클릭 `./setup.sh` 연동 안내 (Priority: P3)

**Goal**: 복원 사후 파일 수록 무결성 검사 수행, 결과 메트릭 출력, 및 `--run-setup` 플래그를 통한 원클릭 `./setup.sh` 연동 구현.

**Independent Test**: `./scripts/unpack_seed.sh --run-setup` 실행 시 복원 완료 후 `./setup.sh` 스크립트가 자동 연동 실행됨을 확인.

### Tests for User Story 3 (MANDATORY) ⚠️

- [x] T009 [P] [US3] Create unit tests for post-unpack file verification and `--run-setup` flag handling in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 3

- [x] T010 [US3] Implement post-unpack file verification and `--run-setup` trigger in `scripts/unpack_seed.sh`

**Checkpoint**: All User Stories (US1, US2, US3) are fully functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full test suite verification

- [x] T011 Run quickstart validation scenarios from `specs/111-unpack-seed-script-enhancement/quickstart.md`
- [x] T012 Run full unit test suite (`uv run pytest tests/unit/`) across all unit tests
- [x] T013 Verify Constitution Principle II & DoD compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion.
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion.
- **User Story 3 (Phase 5)**: Depends on Phase 3 and 4 completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

---

## Implementation Strategy (MVP First)

1. **MVP Scope**: Complete Phase 1 ~ Phase 3 (User Story 1 - Multi-format auto-detection & non-destructive extraction).
2. **Increment 2**: Add Phase 4 (User Story 2 - CLI options & pre-unpack integrity verification).
3. **Increment 3**: Add Phase 5 (User Story 3 - Post-unpack verification & `--run-setup` integration).
4. **Final Polish**: Run `quickstart.md` scenarios and full `uv run pytest tests/unit/` test suite.

---

## Phase 7: Convergence

- [x] T014 Implement file count and restored volume metrics calculation and output in `scripts/unpack_seed.sh` per FR-005 (partial)
- [x] T015 Add extraction benchmark test case measuring .tar.gz and .zip unpack performance (<10s) in `tests/unit/test_shell_scripts.py` per DoD-003, SC-001 (missing)



