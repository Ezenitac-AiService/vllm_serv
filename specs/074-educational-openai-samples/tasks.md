# Tasks: AI 서비스 개발자 교육용 OpenAI API 표준 샘플 코드 리팩토링

**Input**: Design documents from `/specs/074-educational-openai-samples/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 헌법 VII조(의무적 회귀 테스트) 및 실체적 TDD 원칙(헌법 II/III조, Zero Mock)에 의거하여 각 샘플 스크립트별 통합 수렴 테스트 포함.

**Organization**: 각 과제는 유저 스토리(US1, US2, US3)별로 독립 수록되어 독립 구현 및 테스트 가능.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: 병렬 수행 가능 (다른 파일, 미완료 과제에 대한 의존성 없음)
- **[Story]**: 해당 유저 스토리 (US1, US2, US3)

---

## Phase 1: Setup (공통 환경 및 기반)

**Purpose**: 프로젝트 샘플 파일 의존성 및 환경 검증

- [x] T001 Verify samples directory layout and python dependencies in `samples/`
- [x] T002 [P] Inspect `samples/common.py` for any lingering Pydantic imports

---

## Phase 2: Foundational (차단적 전제 과제)

**Purpose**: 비전공자 훈련생 교육을 위한 공통 헬퍼 최소화 및 파이썬 딕셔너리(`dict`) 포맷 기반 정비

- [x] T003 Clean and simplify server health checker & terminal printer in `samples/common.py`

**Checkpoint**: Foundation ready - 유저 스토리별 리팩토링 시작 가능

---

## Phase 3: User Story 1 - 비전공자 훈련생용 표준 Chat Completions 예제 리팩토링 (Priority: P1) 🎯 MVP

**Goal**: Pydantic 의존성을 전면 제거하고 `from openai import OpenAI` 및 파이썬 기본 딕셔너리 기반으로 `sample_01_chat.py` 재작성

**Independent Test**: `uv run python samples/sample_01_chat.py` 실행 시 Pydantic 에러 없이 직관적인 모델 답변 텍스트 수신

### Tests for User Story 1

- [x] T004 [P] [US1] Create integration test for educational chat sample in `tests/integration/test_educational_samples.py`

### Implementation for User Story 1

- [x] T005 [US1] Refactor `samples/sample_01_chat.py` using OpenAI SDK and dict payloads with line-by-line Korean comments
- [x] T006 [US1] Verify `sample_01_chat.py` execution via `uv run python samples/sample_01_chat.py`

**Checkpoint**: User Story 1 (MVP) 독립 수렴 검증 완료

---

## Phase 4: User Story 2 - 모델 파라미터 제어 교육 예제 리팩토링 (Priority: P2)

**Goal**: `temperature`, `top_p`, `stop` 파라미터 설정을 파이썬 기본 딕셔너리 구조와 직관적인 주석으로 `sample_02_model_params.py` 재작성

**Independent Test**: `uv run python samples/sample_02_model_params.py` 실행 시 정지 사유 및 파라미터별 제어 결과가 깔끔하게 콘솔에 출력됨

### Tests for User Story 2

- [x] T007 [P] [US2] Create test for model params sample in `tests/integration/test_educational_model_params.py`

### Implementation for User Story 2

- [x] T008 [US2] Refactor `samples/sample_02_model_params.py` with parameter control explanations in `samples/sample_02_model_params.py`
- [x] T009 [US2] Verify `sample_02_model_params.py` execution via `uv run python samples/sample_02_model_params.py`

**Checkpoint**: User Story 1 및 2 독립 수렴 완료

---

## Phase 5: User Story 3 - RAG 임베딩 및 리랭킹 교육 예제 리팩토링 (Priority: P3)

**Goal**: BGE M3 임베딩(1024차원) 및 Reranker 문서 관련도 점수 추출 샘플을 초급자 눈높이로 `sample_03_embedding.py`, `sample_04_reranking.py` 재작성

**Independent Test**: `uv run python samples/sample_03_embedding.py` 및 `uv run python samples/sample_04_reranking.py` 실행 시 1024차원 수치 및 관련도 점수 반환

### Tests for User Story 3

- [x] T010 [P] [US3] Create test for embedding & reranking samples in `tests/integration/test_educational_auxiliary_samples.py`

### Implementation for User Story 3

- [x] T011 [US3] Refactor `samples/sample_03_embedding.py` for 1024-dim vector extraction in `samples/sample_03_embedding.py`
- [x] T012 [US3] Refactor `samples/sample_04_reranking.py` for BGE reranker scoring in `samples/sample_04_reranking.py`
- [x] T013 [US3] Verify `samples/sample_03_embedding.py` and `samples/sample_04_reranking.py` execution

**Checkpoint**: 모든 유저 스토리 독립 구현 완결

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 비전공자 훈련생 가이드 문서화 및 전체 회귀 수트 검증

- [x] T014 [P] Update non-technical trainee quickstart guide in `samples/README.md`
- [x] T015 Execute full suite regression test via `uv run pytest` per Constitution Article VII

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phase 1 & 2)**: 즉시 시작 가능
- **User Stories (Phase 3+)**: Foundational 완료 후 진행 (US1 -> US2 -> US3 순차 또는 병렬 진행 가능)
- **Polish (Phase 6)**: 모든 유저 스토리 완결 후 진행

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & Foundational)
2. Complete Phase 3 (User Story 1 - `sample_01_chat.py`)
3. **Validate**: `uv run python samples/sample_01_chat.py` 실행으로 Pydantic 없는 직관적 대화 예제 동작 수렴

### Full Delivery

1. Setup + Foundational -> US1 (MVP Chat) -> US2 (Params) -> US3 (Embedding/Rerank) -> README.md
2. Full Suite Regression Test: `uv run pytest`
