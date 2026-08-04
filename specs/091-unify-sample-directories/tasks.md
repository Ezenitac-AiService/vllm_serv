# Tasks: 샘플 실습 디렉토리 이중화 분석 및 표준 통합 (`091-unify-sample-directories`)

**Input**: Design documents from `/specs/091-unify-sample-directories/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/sample_directory_contract.json, quickstart.md

**Tests**: 프로젝트 헌장(Constitution II, VII)에 따라 모든 과제는 `uv run pytest` 기반의 실측 테스트 수트 검증을 거칩니다.

**Organization**: 각 User Story별로 태스크가 분류되어 있어 독립적인 구현 및 검증이 가능합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 수행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 사용자 시나리오 (예: US1, US2, US3)
- 명확한 파일 상대/절대 경로가 명시되어 있습니다.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 환경 검증 및 디렉토리 현황 확인

- [x] T001 현재 `sample/` 물리 디렉토리 및 `samples` 심볼릭 링크 상태 검사 (`ls -la sample samples`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story 구현에 앞서 선행되어야 하는 핵심 인프라 구축

**⚠️ CRITICAL**: 이 단계가 완료되기 전에는 User Story 작업을 시작할 수 없습니다.

- [x] T002 [P] `specs/091-unify-sample-directories/contracts/sample_directory_contract.json` 계약 검증
- [x] T003 [P] `sample/pyproject.toml` 및 `sample/uv.lock` 패키지 구성 파일 무결성 확인

**Checkpoint**: 기본 인프라 확인 완료 - User Story 작업 시작 가능

---

## Phase 3: User Story 1 - 샘플 디렉토리 이중화 원인 분석 및 단일 표준 경로 지정 (Priority: P1) 🎯 MVP

**Goal**: `sample/` 물리 디렉토리를 유일한 표준 경로로 정립하고 임시 생성되었던 `samples` 심볼릭 링크를 안전하게 영구 삭제

**Independent Test**: `samples` 심볼릭 링크가 삭제되어 존재하지 않으며, `sample/` 물리 디렉토리만 단일 존재하는지 실측 검증

### Tests for User Story 1

- [x] T004 [P] [US1] 샘플 디렉토리 통합 구조 검증 테스트 작성 (`tests/test_sample_directory_structure.py`)

### Implementation for User Story 1

- [x] T005 [US1] 임시 생성되었던 `samples` 심볼릭 링크 영구 삭제 (`rm samples`)
- [x] T006 [US1] `sample/` 주 표준 물리 디렉토리 내 22종 고도화 스크립트 무결성 검증

**Checkpoint**: User Story 1 (단일 디렉토리 통합 및 심볼릭 링크 삭제) 독립 검증 완료

---

## Phase 4: User Story 2 - 빌드, 패키징 및 시드팩 파이프라인과의 정합성 통합 (Priority: P2)

**Goal**: `scripts/make_seed_pack.sh` 패키징 스크립트를 정돈하여 시드팩 타르볼 내 `sample/` 단일 물리 디렉토리만 포함되도록 정합성 확보

**Independent Test**: `scripts/make_seed_pack.sh` 실행 시 생성되는 타르볼 내 단일 `sample/` 디렉토리 포함 확인

### Implementation for User Story 2

- [x] T007 [P] [US2] `scripts/make_seed_pack.sh` 스크립트에 `sample/` 물리 디렉토리 번들링 명시 및 이중 압축 예외 정정
- [x] T008 [US2] `make_seed_pack.sh` 스크립트 실행 및 생성된 타르볼(`vllm_serv_seed.tar.gz`) 레이아웃 실측 검증 (T007에 의존)

**Checkpoint**: User Story 1 & 2 통합 패키징 검증 완료

---

## Phase 5: User Story 3 - 샘플 수트 자동화 테스트 수트 정합성 검증 (Priority: P3)

**Goal**: `tests/test_sample_scripts.py` 수트가 `sample/` 단일 물리 디렉토리를 탐색하고 22종 실습 코드 구문 및 dynamic host binding을 검증하도록 보장

**Independent Test**: `uv run pytest tests/test_sample_scripts.py` 수행 시 100% Green (PASSED) 달성

### Implementation for User Story 3

- [x] T009 [P] [US3] `tests/test_sample_scripts.py` 테스트 파일이 `sample/` 단일 경로를 직접 탐색하도록 업데이트
- [x] T010 [US3] `uv run pytest tests/test_sample_scripts.py` 및 `tests/test_sample_directory_structure.py` 수트 실행 및 100% Pass 검증

**Checkpoint**: 모든 User Story (US1, US2, US3) 기능 구현 및 검증 완료

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 종합 검증, 문서 최적화 및 회귀 테스트 완료

- [x] T011 [P] `sample/README.md` 및 `specs/091-unify-sample-directories/quickstart.md` 설명서 가이드 업데이트
- [x] T012 [Quickstart 실측] Quickstart 검증 시나리오 1~3단계 전체 수행 및 DoD(DoD-001~003) 달성 최종 확인

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 실행
- **User Stories (Phase 3+)**: Foundational 완료 후 시작 (US1 → US2 → US3)
- **Polish (Phase 6)**: 모든 User Story 완료 후 실행

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 & 2 완료
2. Phase 3 (User Story 1): `rm samples` 실행 및 `sample/` 디렉토리 무결성 검증
3. `tests/test_sample_directory_structure.py`로 독자 검증 후 MVP 완성
