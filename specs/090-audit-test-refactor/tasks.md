# Tasks: 학습 플랫폼 이관 코드 정밀 검토, 종합 테스트 및 구조적 리팩토링 (`090-audit-test-refactor`)

**Input**: Design documents from `/specs/090-audit-test-refactor/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/cuda_build_api.json, quickstart.md

**Tests**: 프로젝트 헌장(Constitution II, VII)에 따라 모든 구현 과제는 `uv run pytest` 기반의 실측 테스트 작성을 필수 동반합니다.

**Organization**: 각 User Story별로 태스크가 분류되어 있어 독립적인 구현 및 검증이 가능합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 수행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 사용자 시나리오 (예: US1, US2, US3)
- 명확한 파일 상대/절대 경로가 명시되어 있습니다.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 환경 준비 및 디렉토리 구조 확립

- [x] T001 프로젝트 아카이빙 디렉토리 `.legacy/archive_088_sync/` 생성
- [x] T002 `uv` 환경 및 종속성 패키지 정상 구동 검증 (`uv sync`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story 구현에 앞서 선행되어야 하는 핵심 인프라 구축

**⚠️ CRITICAL**: 이 단계가 완료되기 전에는 User Story 작업을 시작할 수 없습니다.

- [x] T003 [P] `specs/090-audit-test-refactor/contracts/cuda_build_api.json` 인터페이스 계약 검증
- [x] T004 [P] 쉘 공통 믹스인 헤더 스크립트 `scripts/common.sh` 초기화
- [x] T005 [P] 파이썬 CUDA 환경 탐지 진입점 모듈 `src/utils/cuda_env.py` 초기 스케일 구현

**Checkpoint**: 기본 인프라 준비 완료 - User Story 구현 시작 가능

---

## Phase 3: User Story 1 - 학습 플랫폼 이관 코드 및 혼재된 자산 전수 조사/정리 (Priority: P1) 🎯 MVP

**Goal**: 학습 플랫폼에서 이관되어 혼재된 파일 자산을 정밀 감사(Audit)하고, 레거시/중복 자산을 `.legacy/archive_088_sync/` 디렉토리로 격리 조치

**Independent Test**: 감사 스크립트 실행 후 자산 목록표 생성 및 `.legacy/archive_088_sync/` 격리 이동 상태 실측 검증

### Tests for User Story 1

- [x] T006 [P] [US1] 자산 전수 감사 및 `.legacy/` 격리 이동 검증 테스트 작성 (`tests/test_asset_inventory.py`)

### Implementation for User Story 1

- [x] T007 [P] [US1] 프로젝트 자산 스캐너 및 감사 스크립트 구현 (`scripts/audit_assets.py`)
- [x] T008 [US1] 감사 스크립트를 실행하여 중복/레거시 파일들을 `.legacy/archive_088_sync/` 디렉토리로 이동 조치 (T006, T007에 의존)
- [x] T009 [US1] 이관 및 정리 결과 감사 리포트 검증 및 workspace 경로 최적화

**Checkpoint**: User Story 1 (자산 정밀 감사 및 정리) 독자적 작동 및 검증 완료

---

## Phase 4: User Story 2 - 혼재 코드 검증 및 자동화 테스트 수트 구축 (Priority: P2)

**Goal**: CUDA GPU 전용 환경 요구사항 검증, llama.cpp 휠 GPU 오프로드 정밀 단정 및 12종 실습 샘플 스크립트 구문/동적 바인딩 테스트 수트 구축

**Independent Test**: `uv run pytest tests/test_cuda_env.py tests/test_sample_scripts.py -v` 실행 시 100% Green (PASSED) 달성 (CUDA GPU 미장착 시 Fail-Fast 중단 확인)

### Tests for User Story 2

- [x] T010 [P] [US2] CUDA GPU 탐지 및 llama.cpp 휠 오프로드 검증 테스트 작성 (`tests/test_cuda_env.py`)
- [x] T011 [P] [US2] 12종 실습 샘플 스크립트(`sample_01`~`06`, `openai_01`~`06`) 구문 및 동적 바인딩 검증 테스트 작성 (`tests/test_sample_scripts.py`)

### Implementation for User Story 2

- [x] T012 [US2] `src/utils/cuda_env.py` 내 NVIDIA 드라이버/CUDA/cuDNN 버전을 정밀 탐지하고 Fail-Fast 단정을 수행하는 `CudaEnvironmentProfile` 로직 구현 (T010에 의존)
- [x] T013 [US2] `scripts/verify_wheel_binary.py` 스크립트를 `src/utils/cuda_env.py` 공통 모듈 참조 방식으로 업데이트 및 GPU 지원 단정 로직 적용

**Checkpoint**: User Story 1 & 2 모두 독자적으로 완벽히 구동 및 검증 완료

---

## Phase 5: User Story 3 - 모듈 구조 개선 및 리팩토링 (Priority: P3)

**Goal**: 파편화된 CUDA/드라이버 탐지 로직을 `src/utils/cuda_env.py` 및 `scripts/common.sh` 공통 모듈로 통합하여 코드 중복 제거

**Independent Test**: `bash -n scripts/*.sh` 및 `uv run pytest` 수행 시 중복 호출 없이 린트/테스트 100% 통과

### Implementation for User Story 3

- [x] T014 [P] [US3] `scripts/common.sh` 쉘 공통 믹스인 스크립트에 CUDA, 드라이버, OS 검사 함수 구현
- [x] T015 [US3] `scripts/setup.sh` 내 중복 탐지 코드를 제거하고 `scripts/common.sh` 믹스인 참조 방식으로 리팩토링 (T014에 의존)
- [x] T016 [US3] `src/` 및 `scripts/` 내 기타 헬퍼 파일들의 파이썬 호출부를 `src/utils/cuda_env.py` 모듈로 통합 치환
- [x] T017 [US3] `uv run ruff check src/ tests/` 린터 검사를 통한 코드 스타일 및 중복 코드 검증

**Checkpoint**: 모든 User Story (US1, US2, US3)의 독립적 기능 및 통합 검증 완료

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 종합 검증, 문서 최적화 및 회귀 테스트 완료

- [x] T018 [P] Quickstart 검증 문서 및 프로젝트 설명서 업데이트 (`specs/090-audit-test-refactor/quickstart.md`)
- [x] T019 [헌장 VII] 프로젝트 전체 회귀 테스트 수트 실행 (`uv run pytest`)
- [x] T020 [Quickstart 실측] Quickstart 검증 시나리오 1~4단계 전체 수행 및 DoD(DoD-001~003) 달성 최종 확인

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 실행 - 모든 User Story를 블로킹함
- **User Stories (Phase 3+)**: Foundational 단계 완료 후 시작 가능
  - 우선순위에 따라 순차 진행 (US1 → US2 → US3)
- **Polish (Phase 6)**: 모든 User Story 완료 후 실행

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 완료 후 시작 (다른 Story에 대한 의존성 없음)
- **User Story 2 (P2)**: Foundational 완료 후 시작 (US1과 독립적으로 검증 가능)
- **User Story 3 (P3)**: Foundational 완료 후 시작 (US1, US2 결과를 바탕으로 모듈 통합 리팩토링)

### Parallel Opportunities

- Phase 1 & 2의 [P] 태스크들 병렬 수행 가능
- US1의 T006, T007 병렬 작성 가능
- US2의 T010, T011 병렬 작성 가능
- US3의 T014 병렬 수행 가능

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup 및 Phase 2 Foundational 완성
2. Phase 3 User Story 1 (자산 정밀 감사 및 `.legacy/` 이동) 실행
3. `tests/test_asset_inventory.py`로 독자 검증 후 MVP 완성

### Incremental Delivery

1. MVP (User Story 1) 완납 → 혼재 자산 정리 완료
2. User Story 2 추가 → CUDA GPU 테스트 수트 및 샘플 코드 동적 바인딩 검증 완료
3. User Story 3 추가 → 공통 모듈 이중화(`cuda_env.py` & `common.sh`) 리팩토링 완성
4. Phase 6 Polish → 회귀 테스트(`uv run pytest`) 및 Quickstart 가이드 전체 실측 검증 완료
