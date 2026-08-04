# Tasks: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 연동 (`095-setup-benchmark-model-selection`)

**Input**: Design documents from `/specs/095-setup-benchmark-model-selection/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/setup_benchmark_contract.json, quickstart.md

**Tests**: 모든 과제는 `uv run pytest` 기반의 실측 및 mock 검증을 거칩니다.

**Organization**: 각 User Story별로 태스크가 분류되어 있어 독립적인 구현 및 검증이 가능합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 수행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 사용자 시나리오 (예: US1, US2)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 벤치마크 셋업 계약 및 데이터 인프라 준비

- [X] T001 `specs/095-setup-benchmark-model-selection/contracts/setup_benchmark_contract.json` 계약 스키마 검증

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 4단계 모듈화 파이프라인 핵심 백엔드 모듈 구현

**⚠️ CRITICAL**: 이 단계가 완료되기 전에는 User Story 작업을 시작할 수 없습니다.

- [X] T002 [P] `scripts/benchmark_context_window.py` 파이썬 모듈 신규 구현 (Stage 2: GGUF 무결성 검증, Stage 3: 컨텍스트 윈도우 2K~16K 실측 VRAM/TPS 측정 및 Stage 4: 추천 모델/컨텍스트 산출)
- [X] T003 [P] `src/core/config_manager.py`에 `auto_benchmark_profile` 원자적 `config/server_config.json` 업데이트 메소드 지원

**Checkpoint**: 4단계 벤치마크 모듈 구축 완료 - User Story 작업 시작 가능

---

## Phase 3: User Story 1 - `setup.sh` 4단계 모듈화 파이프라인 연동 (Priority: P1) 🎯 MVP

**Goal**: `./setup.sh` 실행 시 Step 2.8을 통해 4단계 파이프라인(다운로드 → 무결성 검증 → 컨텍스트 측정 → 설정 반영)을 원스톱 가동

**Independent Test**: `./setup.sh` 구동 시 Step 2.8의 4개 모듈식 단계가 순차 실행되고 `config/server_config.json`에 최적 모델/컨텍스트가 자동 반영되는지 검증

### Tests for User Story 1

- [X] T004 [P] [US1] 4단계 파이프라인 셋업 연동 단위/통합 테스트 수트 구현 (`tests/unit/test_setup_benchmark_integration.py`)

### Implementation for User Story 1

- [X] T005 [US1] `scripts/setup.sh`에 Step 2.8 (4단계 모듈식 파이프라인 연동: `ensure_models.py` → `verify_model_integrity` → `benchmark_context_window.py` → `save_benchmark_profile`) 구현 (FR-001, FR-002, FR-003)

**Checkpoint**: User Story 1 (4단계 모듈식 벤치마크 셋업 파이프라인) 연동 완료

---

## Phase 4: User Story 2 - `--skip-benchmark` 및 비대화형 CI/CD 지원 (Priority: P2)

**Goal**: `--skip-benchmark` 플래그 및 비대화형 환경 자동 타임아웃/폴백 처리 구현

**Independent Test**: `./setup.sh --skip-benchmark` 구동 시 Stage 3 실측 벤치마크를 건너뛰고 15초 이내 완료되는지 검증

### Implementation for User Story 2

- [X] T006 [P] [US2] `scripts/setup.sh`에 `--skip-benchmark` CLI 플래그 파싱 및 Stage 3 벤치마크 스킵 분기 연동 (FR-004)
- [X] T007 [P] [US2] `scripts/benchmark_context_window.py`에 비대화형 타임아웃(120초) 및 OOM 발생 시 안전 기본 프로파일(qwen3.5-4b, 4096 context) 폴백 처리 추가
- [X] T008 [US2] `tests/unit/test_setup_benchmark_integration.py`에 `--skip-benchmark` 및 폴백 검증 테스트 케이스 추가

**Checkpoint**: User Story 1 & 2 완료

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 최종 문서화 및 DoD 검증 수행

- [X] T009 [P] `specs/095-setup-benchmark-model-selection/quickstart.md` 가이드 문서 업데이트
- [X] T010 [Quickstart 실측] Quickstart 시나리오 1~3 전체 수행 및 DoD(DoD-001~003) 달성 최종 검증

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 실행
- **User Stories (Phase 3+)**: Foundational 완료 후 시작 (US1 → US2)
- **Polish (Phase 5)**: 모든 User Story 완료 후 실행
