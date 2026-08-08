# Tasks: README.md 전면 재작성 (Rewrite README.md for LLM/Web Server & Operational Scripts)

**Input**: Design documents from `/specs/115-rewrite-readme-documentation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in all descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification of task environment and feature directory structure

- [x] T001 Verify feature specification and design documents in `specs/115-rewrite-readme-documentation/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Source code and script parameter audit to guarantee 100% accurate documentation

- [x] T002 Inspect root shell scripts, `scripts/`, and `src/` modules to verify CLI flags and API endpoints for documentation accuracy

**Checkpoint**: Foundational audit ready - README.md rewriting can now begin.

---

## Phase 3: User Story 1 - 에이전트 내부 개발 내용 제거 및 핵심 개요/Quick Start 정립 (Priority: P1) 🎯 MVP

**Goal**: 에이전트/Speckit 커맨드 설명을 전면 제거하고 3단계 Quick Start 가이드 및 Mermaid 시스템 아키텍처 다이어그램 수록

**Independent Test**: `README.md` 상단에서 3-Step Quick Start 가이드 및 Mermaid 다이어그램 확인 및 에이전트 용어 0건 검증

### Implementation for User Story 1

- [x] T003 [P] [US1] Draft Title, Project Overview, Mermaid System Architecture Diagram, and 3-Step Quick Start guide in `README.md`

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and readable.

---

## Phase 4: User Story 2 - 루트 제어 쉘 스크립트 6종 가이드 작성 (Priority: P1) 🎯 MVP

**Goal**: 프로젝트 루트 6대 제어 쉘 스크립트(`make_seed_pack.sh`, `setup.sh`, `start_server.sh`, `status_server.sh`, `stop_server.sh`, `unpack_seed.sh`) 역할 및 옵션 명세화

**Independent Test**: 6개 쉘 스크립트 각각의 사용 예시와 CLI 인자(`--force-build`, `--wheel-path` 등) 매칭 확인

### Implementation for User Story 2

- [x] T004 [P] [US2] Add Root Control Scripts section covering all 6 shell scripts with complete CLI flags and execution examples in `README.md`

**Checkpoint**: User Stories 1 AND 2 are both complete.

---

## Phase 5: User Story 3 - scripts/ 유틸리티 및 src/ 아키텍처 설명 수록 (Priority: P2)

**Goal**: `scripts/` 디렉터리 파이썬/쉘 도구 및 `src/` 디렉터리 LLM 서빙 엔진 & Web 대시보드 아키텍처 설명 수록

**Independent Test**: `scripts/benchmark_context_window.py` 등 보조 도구 사용법 및 `src/core/`, `src/api/` 엔드포인트 수록 확인

### Implementation for User Story 3

- [x] T005 [P] [US3] Add `scripts/` directory tools guide and `src/` directory core engine & web server architecture specs in `README.md`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Markdown verification, link validation, and regression testing

- [x] T006 Verify `README.md` contains zero agent/speckit keywords using `grep -iE "speckit|slash command" README.md`
- [x] T007 Run full unit regression test suite `uv run pytest tests/unit/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on US1 completion.
- **User Story 3 (Phase 5)**: Depends on US2 completion.
- **Polish (Phase 6)**: Depends on US1, US2, US3 completion.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1 & Phase 2 audit.
2. Draft Overview, Quick Start, and Root 6 Shell Scripts sections in `README.md`.
3. Validate MVP documentation structure.

### Incremental Delivery

1. Complete US1 & US2 -> Core Operational Guide Ready.
2. Complete US3 -> Full Architecture & Utility Tools Guide Complete.
3. Run Phase 6 polish & verification.
