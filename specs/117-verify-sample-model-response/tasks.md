# Tasks: sample 예제 스크립트 호출 모델 대 응답 모델 일치성 검증 및 하드코딩 제거

**Input**: Design documents from `/specs/117-verify-sample-model-response/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/  

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify configuration schema and base test environment

- [x] T001 Verify current `sample/config.json` schema and test environment configuration in `sample/config.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core `sample/config.json` SSOT consolidation for all sample scripts

- [x] T002 Update `sample/config.json` to include full SSOT server candidates (`10.0.0.41`, `192.168.0.175`, `127.0.0.1`) and timeout configs in `sample/config.json`

---

## Phase 3: User Story 2 - sample/ 폴더 코드 내 하드코딩 및 더미 목업 전면 제거 (Priority: P1) 🎯 MVP

**Goal**: `sample/` 내 모든 파이썬 파일의 하드코딩된 IP, 포트, 모델 리스트, 타임아웃, 목업 텍스트를 제거하고 `sample/config.json` 단일 진실 출처로 전환한다.

**Independent Test**: `sample/` 폴더 내 `.py` 소스 코드 정규식 검사 시 하드코딩 IP/모델 리스트/목업 텍스트 0건 단정 및 정상 실행.

### Implementation for User Story 2

- [x] T003 [P] [US2] Refactor `sample/common.py` to load server host candidates, ports, and benchmarks dynamically from `sample/config.json`
- [x] T004 [P] [US2] Remove hardcoded fallback model lists and timeouts in `sample/sample_04_model_switch.py` to use `load_sample_config()`
- [x] T005 [P] [US2] Remove hardcoded fallback model lists and timeouts in `sample/openai_04_model_switch.py` to use `load_sample_config()`

**Checkpoint**: User Story 2 complete - `sample/` folder code relies 100% dynamically on `sample/config.json`.

---

## Phase 4: User Story 3 - API Gateway 응답 객체 모델 필드 정합성 보장 (Priority: P1) 🎯 MVP

**Goal**: `POST /v1/chat/completions` MOCK 및 프록시 응답 처리 시 요청 페이로드의 `model` ID가 응답 JSON의 `model` 필드에 동적으로 대입되도록 보장한다.

**Independent Test**: `uv run pytest tests/unit/test_dynamic_model_switch.py` MOCK 서빙 시 요청된 모델 ID가 응답 `model`에 반환됨을 검증.

### Implementation for User Story 3

- [x] T006 [P] [US3] Ensure `MOCK_LLAMA_SERVER=1` response generator in `src/api/routes/inference_api.py` sets `model` field dynamically from request payload

**Checkpoint**: User Story 3 complete - Gateway response JSON contains matching requested `model` ID.

---

## Phase 5: User Story 1 - sample 실습 스크립트 실행 시 호출 모델 대 응답 모델 일치 검증 및 시각화 (Priority: P1) 🎯 MVP

**Goal**: 실습 스크립트 실행 시 응답 객체 내 `model` 필드를 추출하여 요청 모델과 비교하고 `[모델 검증: 요청(X) == 응답(X) ✅]` 로그를 시각적으로 출력한다.

**Independent Test**: `uv run python sample/sample_04_model_switch.py` 및 `uv run python sample/openai_04_model_switch.py` 실행 시 콘솔에 일치 검증 로그 표출.

### Implementation for User Story 1

- [x] T007 [P] [US1] Update `print_performance_summary` in `sample/common.py` to render requested vs responded model validation tag `[모델 검증: 요청(X) == 응답(Y) ✅/❌]`
- [x] T008 [P] [US1] Implement model response parity validation and visual logging in `sample/sample_04_model_switch.py`
- [x] T009 [P] [US1] Implement model response parity validation and visual logging in `sample/openai_04_model_switch.py`

**Checkpoint**: User Story 1 complete - sample scripts display live model parity validation results clearly.

---

## Phase 6: User Story 4 - 샘플 스크립트 응답 모델 일치 자동화 단위 테스트 (Priority: P2)

**Goal**: 하드코딩 0건 검사 및 호출 모델 대 응답 모델 교차 검증 단위 테스트 수록.

**Independent Test**: `uv run pytest tests/unit/test_sample_model_switch.py` 100% 통과.

### Implementation for User Story 4

- [x] T010 [P] [US4] Add regex scanner test in `tests/unit/test_sample_model_switch.py` to verify zero hardcoded IPs/magic numbers in `sample/`
- [x] T011 [P] [US4] Add unit test asserting requested vs responded model ID parity in `tests/unit/test_sample_model_switch.py`

**Checkpoint**: User Story 4 complete - automated regression tests verify zero hardcoding and model parity.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Full regression suite validation and quickstart scenario checks

- [x] T012 Run full unit test suite via `uv run pytest tests/unit/ --ignore=tests/unit/test_legacy_extraction_llm.py --ignore=tests/unit/test_e2e_serving.py --ignore=tests/unit/test_embedding_reranker_serving.py`
- [x] T013 Execute end-to-end validation scenarios documented in `specs/117-verify-sample-model-response/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 2 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 3 (Phase 4)**: Can run in parallel with US2 after Foundational completion
- **User Story 1 (Phase 5)**: Depends on US2 and US3 completion
- **User Story 4 (Phase 6)**: Depends on US1 completion
- **Polish (Phase 7)**: Depends on Phase 3 through Phase 6 completion

---

## Implementation Strategy

### MVP Scope

1. Complete Phase 1 (Setup) & Phase 2 (Foundational)
2. Complete Phase 3 (US2 - Remove Hardcoding in `sample/`) & Phase 4 (US3 - Gateway Response Model Parity)
3. Complete Phase 5 (US1 - Model Parity Verification Logging in `sample/`)
4. Validate MVP with `uv run python sample/sample_04_model_switch.py`
5. Complete Phase 6 (Automated Unit Tests) & Phase 7 (Regression Suite)
