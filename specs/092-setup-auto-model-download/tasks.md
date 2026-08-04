# Tasks: `setup.sh` 필수 GGUF 모델 자동 점검 및 자동 다운로드 통합 (`092-setup-auto-model-download`)

**Input**: Design documents from `/specs/092-setup-auto-model-download/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/ensure_models_contract.json, quickstart.md

**Tests**: 프로젝트 헌장(Constitution II, VII)에 따라 모든 과제는 `uv run pytest` 기반의 실측 테스트 수트 검증을 거칩니다.

**Organization**: 각 User Story별로 태스크가 분류되어 있어 독립적인 구현 및 검증이 가능합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 수행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 사용자 시나리오 (예: US1, US2, US3)
- 명확한 파일 상대/절대 경로가 명시되어 있습니다.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 환경 검증 및 모델 디렉토리 현황 확인

- [x] T001 `models/` 디렉토리 존재 확인 및 `config/model_catalog.json` 카탈로그 스키마 검증
- [x] T002 `src/core/model_downloader.py` 기존 다운로더 모듈의 다운로드 API 검증

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story 구현에 앞서 선행되어야 하는 핵심 인프라 구축

**⚠️ CRITICAL**: 이 단계가 완료되기 전에는 User Story 작업을 시작할 수 없습니다.

- [x] T003 [P] `specs/092-setup-auto-model-download/contracts/ensure_models_contract.json` 인터페이스 계약 검증
- [x] T004 [P] `scripts/common.sh` 쉘 공통 믹스인의 GPU/드라이버 검사 함수 검증

**Checkpoint**: 기본 인프라 확인 완료 - User Story 작업 시작 가능

---

## Phase 3: User Story 1 - `setup.sh` 가동 시 필수 GGUF 모델 유무 자동 검사 및 다운로드 연동 (Priority: P1) 🎯 MVP

**Goal**: `scripts/ensure_models.py` 헬퍼 스크립트를 작성하여 3종 필수 GGUF 모델(`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`) 유무를 점검하고 부재 시 자동 다운로드하여 `scripts/setup.sh` 파이프라인에 통합

**Independent Test**: `models/`가 비어있는 상태에서 `uv run python scripts/ensure_models.py` 실행 시 3종 모델이 `models/`에 자동 다운로드되는지 검증

### Tests for User Story 1

- [x] T005 [P] [US1] 모델 점검 및 다운로드 헬퍼 테스트 작성 (`tests/test_ensure_models.py`)

### Implementation for User Story 1

- [x] T006 [P] [US1] `src/core/model_downloader.py` 모듈을 연동하는 파이썬 헬퍼 스크립트 구현 (`scripts/ensure_models.py`)
- [x] T007 [US1] `scripts/setup.sh` 파이프라인에 `uv run python scripts/ensure_models.py` 단계 통합 (T006에 의존)

**Checkpoint**: User Story 1 (모델 자동 점검 및 프로비저닝) 독립 검증 완료

---

## Phase 4: User Story 2 - 스마트 스킵 및 다운로드 상태 표시 (Priority: P2)

**Goal**: `models/`에 이미 모델이 존재하는 경우 1초 이내에 재다운로드를 스킵(Smart Skip)하고, 다운로드 중에는 진행률 및 결과를 명확히 표시

**Independent Test**: 모델이 배치된 상태에서 `uv run python scripts/ensure_models.py` 재실행 시 2초 이내 스킵 성공

### Implementation for User Story 2

- [x] T008 [P] [US2] `scripts/ensure_models.py`에 파일 크기 정밀 검증 및 스마트 스킵(Smart Skip) 로직 구현
- [x] T009 [US2] 이미 존재할 때 고속 스킵 시나리오를 `tests/test_ensure_models.py`에 추가하여 검증 (T008에 의존)

**Checkpoint**: User Story 1 & 2 고속 스킵 및 프로비저닝 검증 완료

---

## Phase 5: User Story 3 - PCI 하드웨어 탐지 및 `scripts/` 전수 원스톱 파이프라인 체이닝 (Priority: P3)

**Goal**: `scripts/setup.sh`에 `lspci` 기반 PCI 물리 GPU 장비 탐지, `update_cuda_drivers.sh`, `seed_db.py`, `audit_assets.py`, `configure_firewall.sh` 체이닝을 구성하여 원스톱 Zero-Touch 셋업 완성

**Independent Test**: `./setup.sh` 실행 시 PCI 탐지부터 드라이버/DB/휠/모델/방화벽까지 원스톱으로 완수되는지 검증

### Implementation for User Story 3

- [x] T010 [P] [US3] `scripts/setup.sh`에 `lspci | grep -i nvidia` 물리 GPU 탐지 및 `scripts/update_cuda_drivers.sh` 자동 가이드 연동 구현
- [x] T011 [US3] `scripts/setup.sh`에 `scripts/seed_db.py` DB 초기화 및 `scripts/audit_assets.py` 자산 정돈 단계 체이닝 구성 (T010에 의존)

**Checkpoint**: 모든 User Story (US1, US2, US3) 원스톱 파이프라인 통합 완료

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 종합 검증, 문서 최적화 및 회귀 테스트 완료

- [x] T012 [P] `specs/092-setup-auto-model-download/quickstart.md` 검증 가이드 문서 업데이트
- [x] T013 [Quickstart 실측] Quickstart 검증 시나리오 1~4단계 전체 수행 및 DoD(DoD-001~003) 달성 최종 확인

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
2. Phase 3 (User Story 1): `scripts/ensure_models.py` 작성 및 `setup.sh` 연동
3. `tests/test_ensure_models.py`로 3종 모델 프로비저닝 독자 검증 후 MVP 완성
