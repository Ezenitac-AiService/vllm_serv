# Tasks: `README.md` 프로젝트 설명, 셋업 파이프라인, 제어 쉘 명령 및 수동 스크립트 가이드 고도화 명세 (103-readme-documentation-enhancement)

**Input**: Design documents from `/specs/103-readme-documentation-enhancement/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project documentation structure initialization and contract schema verification

- [X] T001 Verify contract schema `specs/103-readme-documentation-enhancement/contracts/readme-structure-schema.json` against README structure requirements

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core repository verification that MUST be complete before documentation updates

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Verify current repository scripts (`setup.sh`, `start_server.sh`, `stop_server.sh`, `status_server.sh`, `scripts/ensure_models.py`, `.specify/scripts/bash/create-new-feature.sh`) to ensure accurate documentation references

**Checkpoint**: Foundation ready - user story documentation tasks can now begin.

---

## Phase 3: User Story 1 - 프로젝트 개요 및 셋업 파이프라인 명세 고도화 (Priority: P1) 🎯 MVP

**Goal**: Structure project overview and 9-stage setup pipeline Mermaid flowchart in `README.md`.

**Independent Test**: Check Overview section and 9-stage setup pipeline Mermaid flowchart in `README.md`.

### Implementation for User Story 1

- [X] T003 [P] [US1] Structure and update project overview section in `README.md` including GPU 100% VRAM offload and OpenAI REST API compatibility
- [X] T004 [US1] Create Mermaid flowchart and detailed descriptions for 9-stage setup pipeline in `README.md`

**Checkpoint**: User Story 1 complete - Overview and 9-stage setup pipeline documented.

---

## Phase 4: User Story 2 - 서버 셋업 및 상태 변경 제어 쉘 명령 가이드 명세 (Priority: P1)

**Goal**: Document shell command execution examples for `./setup.sh`, `./start_server.sh`, `./stop_server.sh`, and `./status_server.sh`.

**Independent Test**: Verify `./setup.sh` flags and server control scripts (`start_server.sh`, `stop_server.sh`, `status_server.sh`) usage guide in `README.md`.

### Implementation for User Story 2

- [X] T005 [P] [US2] Update `./setup.sh` command examples and option flags (`--skip-benchmark`) section in `README.md`
- [X] T006 [US2] Add server lifecycle control scripts reference table and command examples (`start_server.sh`, `stop_server.sh`, `status_server.sh`) in `README.md`

**Checkpoint**: User Story 2 complete - Server setup and state transition shell control scripts documented.

---

## Phase 5: User Story 3 - 주요 헬퍼 스크립트 수동 실행 예시 및 파라미터 설명 명세 (Priority: P2)

**Goal**: Document manual execution examples and CLI parameter reference tables for 6 core helper scripts (`ensure_models.py`, `benchmark_context_window.py`, `benchmark_quality.py`, `make_seed_pack.sh`, `configure_firewall.sh`, `create-new-feature.sh`).

**Independent Test**: Verify manual execution examples and CLI parameter reference tables in `README.md`.

### Implementation for User Story 3

- [X] T007 [P] [US3] Add manual execution examples for backend helper scripts (`scripts/ensure_models.py`, `scripts/benchmark_context_window.py`, `scripts/benchmark_quality.py`, `make_seed_pack.sh`, `scripts/configure_firewall.sh`) in `README.md`
- [X] T008 [P] [US3] Add SpecKit manual execution guide and parameter reference table for `.specify/scripts/bash/create-new-feature.sh` in `README.md`
- [X] T009 [US3] Create CLI parameter reference tables for all manual helper scripts detailing parameter names, types, defaults, and descriptions in `README.md`

**Checkpoint**: User Story 3 complete - Manual helper script execution examples and CLI parameter tables documented.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation formatting and validation

- [X] T010 [P] Validate GFM formatting, Mermaid diagram rendering, and Markdown table alignment in `README.md`
- [X] T011 Run quickstart validation scenarios (`specs/103-readme-documentation-enhancement/quickstart.md`) and verify documentation integrity

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
- **User Story 3 (Phase 5)**: Depends on User Story 2 completion
- **Polish (Phase 6)**: Depends on User Story 1, 2, & 3 completion

### Parallel Opportunities

- T003, T005, T007, T008, T010 can run in parallel (editing different Markdown sections).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & Foundational repository script verification)
2. Complete Phase 3 (User Story 1 - Overview and 9-stage setup pipeline)
3. Validate User Story 1 independently in `README.md`

### Full Feature Delivery

1. Complete User Story 1 (Overview & 9-stage setup pipeline)
2. Complete User Story 2 (Setup & server control shell scripts)
3. Complete User Story 3 (Manual helper scripts & CLI parameter tables)
4. Run Phase 6 Polish & quickstart validation scenarios
