# Tasks: `scripts/` 디렉토리 스크립트 모듈화 및 결합도 완화 대대적 리팩토링 (`093-refactor-scripts-architecture`)

**Input**: Design documents from `/specs/093-refactor-scripts-architecture/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/script_architecture_contract.json, quickstart.md

**Tests**: 프로젝트 헌장(Constitution II, VII)에 따라 모든 과제는 `uv run pytest` 기반의 실측 정적 스캔 및 실행 검증을 거칩니다.

**Organization**: 각 User Story별로 태스크가 분류되어 있어 독립적인 구현 및 검증이 가능합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 수행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 사용자 시나리오 (예: US1, US2, US3)
- 명확한 파일 상대/절대 경로가 명시되어 있습니다.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: `scripts/` 디렉토리 전수 정적 스캔 및 의존성 인벤토리 수립

- [x] T001 `scripts/` 디렉토리 내 14개 전체 스크립트 정적 스캔 및 외부 디렉토리(`src/`, `config/`, `data/`) 결합도 인벤토리 구축
- [x] T002 `specs/093-refactor-scripts-architecture/contracts/script_architecture_contract.json` 아키텍처 계약 검증

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 스크립트 리팩토링에 공유되는 `common.sh` 공통 믹스인 강화

**⚠️ CRITICAL**: 이 단계가 완료되기 전에는 User Story 작업을 시작할 수 없습니다.

- [x] T003 [P] `scripts/common.sh`에 SRE 안전 래퍼 함수(`try_optional_step`) 구현 및 예외 로깅 믹스인 추가 (FR-007)
- [x] T004 [P] `scripts/common.sh`에 DevSecOps Cascade 포트 결정 믹스인(`get_configured_port`) 구현 (FR-008)

**Checkpoint**: 공통 믹스인 수립 완료 - User Story 작업 시작 가능

---

## Phase 3: User Story 1 - `scripts/` 내 쉘/파이썬 스크립트의 외부 폴더 직결합 완화 및 모듈화 (Priority: P1) 🎯 MVP

**Goal**: 외부 폴더 하드코딩 참조 경로를 파라미터 주입 및 `common.sh` 믹스인으로 치환하여 결합도 대폭 완화

**Independent Test**: 정적 스캐너 실행 시 `scripts/` 내 타 디렉토리 하드코딩 참조 건수가 80% 이상 감소하는지 검증

### Tests for User Story 1

- [x] T005 [P] [US1] 스크립트 아키텍처 결합도 정적 분석 및 호환성 검증 수트 구현 (`tests/test_script_architecture.py`)

### Implementation for User Story 1

- [x] T006 [P] [US1] `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh` 제어 스크립트의 포트/경로 조회를 `common.sh` 믹스인으로 리팩토링
- [x] T007 [P] [US1] `scripts/ensure_models.py`, `scripts/seed_db.py`, `scripts/audit_assets.py` 파이썬 헬퍼의 외부 경로 지정을 파라미터화로 추상화

**Checkpoint**: User Story 1 (결합도 완화 및 믹스인 연동) 독립 검증 완료

---

## Phase 4: User Story 2 - 비대 스크립트 모듈 분할 및 중복 코드 병합 (Priority: P2)

**Goal**: 800줄 이상의 비대한 `scripts/setup.sh` 및 `scripts/make_seed_pack.sh`를 단일 책임 서브 함수로 분할하고 `|| true` 오염 구문을 `try_optional_step`으로 치환

**Independent Test**: `./setup.sh` 실행 시 라인 수가 40% 이상 감소하고 옵셔널 단계가 안전하게 수행되는지 검증

### Implementation for User Story 2

- [x] T008 [P] [US2] `scripts/setup.sh` 메인 스크립트를 단계별 서브 함수로 분할하고 `try_optional_step` 안전 래퍼 적용 (FR-003, FR-006, FR-007)
- [x] T009 [P] [US2] `scripts/make_seed_pack.sh` 및 `scripts/configure_firewall.sh`를 `common.sh` 믹스인으로 리팩토링 및 예외 회피 정돈 (FR-006)
- [x] T010 [US2] `setup.sh` 라인 수 축소(40% 이상) 및 CLI 인터페이스 호환성 테스트 통과 확인 (T008, T009에 의존)

**Checkpoint**: User Story 1 & 2 모듈화 및 회피 구문 정돈 완료

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 종합 검증, 문서 최적화 및 회귀 테스트 완료

- [x] T011 [P] `specs/093-refactor-scripts-architecture/quickstart.md` 검증 가이드 문서 업데이트
- [x] T012 [Quickstart 실측] Quickstart 검증 시나리오 1~4단계 전체 수행 및 DoD(DoD-001~003) 달성 최종 확인

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 실행
- **User Stories (Phase 3+)**: Foundational 완료 후 시작 (US1 → US2)
- **Polish (Phase 5)**: 모든 User Story 완료 후 실행

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 & 2 완료 (`common.sh` 믹스인 강화)
2. Phase 3 (User Story 1): 스크립트 직결합 제거 및 `tests/test_script_architecture.py` 작성
3. 정적 결합도 스캔 통과 후 MVP 완료
