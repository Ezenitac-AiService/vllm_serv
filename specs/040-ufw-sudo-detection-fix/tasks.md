# Tasks: ufw 방화벽 권한 점검, 바이너리 재빌드 스킵 및 컨텍스트 스케일링 캐싱 (040-ufw-sudo-detection-fix)

**Input**: Design documents from `/specs/040-ufw-sudo-detection-fix/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/benchmark-api.json, quickstart.md

**Tests**: Tests are MANDATORY per Constitution v1.4.0 (Anti-Mock Discipline & Strict `uv run` verification).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and specification structure verification

- [x] T001 Verify project specification files and environment in `specs/040-ufw-sudo-detection-fix/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared testing utilities and foundational test framework

- [x] T002 [P] Create/verify test structure for Anti-Mock real verification in `tests/unit/test_firewall_manager.py` and `tests/unit/test_shell_scripts.py`

---

## Phase 3: User Story 1 - ufw status sudo 감지 및 3초 컴파일 Bypass (Priority: P1) 🎯 MVP

**Goal**: 일반 유저 계정에서 ufw status 권한 부족으로 인한 오감지 차단 및 연속 setup.sh 구동 시 3초 이내 완납 보장

**Independent Test**: ufw 활성화 서버에서 일반 유저 계정으로 `./scripts/setup.sh` 구동 시 `sudo ufw status`로 ufw 활성화 인식 및 2회차 연속 실행 소요 시간 3초 이내 실측 검증

### Tests for User Story 1 (MANDATORY)

- [x] T003 [P] [US1] Add unit & real execution tests for `sudo ufw status` and `sudo -n ufw status` fallback in `tests/unit/test_firewall_manager.py`
- [x] T004 [P] [US1] Add integration test for setup.sh 2nd run 3-second completion in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 1

- [x] T005 [US1] Implement `sudo ufw status` and `sudo firewall-cmd --state` checking logic in `scripts/setup.sh`
- [x] T006 [US1] Implement `sudo -n ufw status` fallback and detection order in `src/core/firewall_manager.py`
- [x] T007 [US1] Remove `--force-reinstall --no-cache-dir` and add Pre-Check `llama_supports_gpu_offload()` CUDA bypass in `scripts/setup.sh`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Seed Pack 휠 검증 및 컨텍스트 프로필 제외 (Priority: P2)

**Goal**: `make_seed_pack.sh` 실행 시 유효한 i7-930 휠 검증 오류 수정 및 `config/model_context_profiles.json` 패키징 원천 제외

**Independent Test**: `make_seed_pack.sh` 구동 시 기존 휠 검증 통과 및 `tar -ztvf` 검사 시 `model_context_profiles.json`이 아카이브에 수록되지 않음을 검증

### Tests for User Story 2 (MANDATORY)

- [x] T008 [P] [US2] Add wheel inspection test and seed pack archive exclusion test in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 2

- [x] T009 [US2] Fix shared library (`.so`) path matching pattern inside zip entry inspection in `scripts/verify_wheel_binary.py`
- [x] T010 [US2] Update tar command in `scripts/make_seed_pack.sh` to include `--exclude="config/model_context_profiles.json"`

**Checkpoint**: User Stories 1 AND 2 are both functional independently.

---

## Phase 5: User Story 3 - CLI & Web UI Dual 인터페이스 컨텍스트 윈도우 스케일링 벤치마크 (Priority: P3)

**Goal**: CLI 스크립트 및 웹 대시보드(Port 8089) UI/REST API 양쪽에서 차분/전수 컨텍스트 윈도우 스케일링 벤치마크 갱신 및 캐시 재사용 구현

**Independent Test**: `setup.sh` Step 4.5에서 캐시 존재 시 벤치마크 스킵, 신규 모델 추가 시 차분 측정, 웹 대시보드 `POST /api/benchmark/rerun` 구동 시 비동기 갱신 실측

### Tests for User Story 3 (MANDATORY)

- [x] T011 [P] [US3] Add contract test for Web Dashboard benchmark endpoints (`GET /api/benchmark/profiles`, `POST /api/benchmark/rerun`) in `tests/unit/test_web_dashboard.py`

### Implementation for User Story 3

- [x] T012 [US3] Implement incremental model benchmark logic and cache verification in `scripts/benchmark_quality.py`
- [x] T013 [US3] Integrate cache check and incremental update step into `scripts/setup.sh` Step 4.5
- [x] T014 [US3] Implement `GET /api/benchmark/profiles` and `POST /api/benchmark/rerun` API routes in `src/web/dashboard.py`
- [x] T015 [US3] Add `[컨텍스트 스케일링 재측정]` button and profile status card to Web Dashboard UI in `src/web/dashboard.py`

**Checkpoint**: All user stories are independently functional with Dual CLI and Web UI interfaces.

---

## Phase 6: Polish & Anti-Mock Converge Verification

**Purpose**: End-to-end verification and quickstart scenario execution

- [x] T016 Execute full pytest test suite using `uv run pytest` across unit and real execution tests
- [x] T017 Run end-to-end validation scenarios documented in `specs/040-ufw-sudo-detection-fix/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Story 1 (Phase 3)**: Depends on Foundational completion (MVP!).
- **User Story 2 (Phase 4)**: Depends on Foundational completion.
- **User Story 3 (Phase 5)**: Depends on Foundational completion.
- **Polish (Phase 6)**: Depends on User Stories 1, 2, and 3 completion.

### Parallel Opportunities

- T003, T004 (US1 Tests) can run in parallel.
- T008 (US2 Test) can run in parallel with US1 implementation.
- T011 (US3 API Test) can run in parallel with CLI implementation.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2.
2. Complete Phase 3 (User Story 1).
3. **STOP and VALIDATE**: Verify `./scripts/setup.sh` sudo ufw detection and 3-second 2nd-run completion.

### Incremental Delivery

1. Deliver MVP (US1: ufw sudo detection & build bypass).
2. Deliver US2 (Seed pack wheel fix & context profile exclusion).
3. Deliver US3 (CLI & Web UI Dual context window scaling benchmark management).
