# Tasks: 멀티 플랫폼 하드웨어 사양(16GB RAM) 및 서브넷 네트워크 토폴로지(10.0.0.x vs 192.168.0.x) 보정 (028-update-platform-network-profiles)

**Input**: Design documents from `/specs/028-update-platform-network-profiles/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Pytest unit tests for profile validation, subnet filters, dynamic VRAM binding, and context limit checks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- File paths are included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project baseline and environment configuration

- [x] T001 Verify configuration layout in `config/platform_profiles.json` and `config/server_config.json`
- [x] T002 Verify Python environment and dependencies using `uv sync`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base types and configuration models required before user story implementation

- [x] T003 [P] Audit `ServerConfig` models and validation rules in `src/core/config_manager.py`
- [x] T004 [P] Audit active network scanning and subnet filtering in `src/core/network_detector.py`

---

## Phase 3: User Story 1 - 플랫폼 하드웨어 프로필(RAM 16GB) 및 서브넷 네트워크 토폴로지 정밀 반영 (Priority: P1) 🎯 MVP

**Goal**: Platform B 물리 RAM 사양 16GB 정정, 개발망(`10.0.0.0/8`) 및 훈련/서비스망(`192.168.0.0/16`) 서브넷 반영, static VRAM 11264MB 하드코딩 제거 및 `VLLM_ADMIN_SECRET` 오버라이드 지원, 컨텍스트 스케일링 상한 제어 (소형 8K~16K / 대형 4K) 및 HTTP 400 에러 처리, `setup.sh` Non-blocking 연동을 완수합니다.

**Independent Test**: `uv run pytest tests/unit/test_config_manager_profiles.py tests/unit/test_network_detector.py tests/unit/test_config_manager.py tests/unit/test_context_scaling_limits.py`

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T005 [P] [US1] Add 16GB RAM and allowed subnets verification tests in `tests/unit/test_config_manager_profiles.py`
- [x] T006 [P] [US1] Add CIDR subnet filtering tests for `10.0.0.0/8` and `192.168.0.0/16` in `tests/unit/test_network_detector.py`
- [x] T007 [P] [US1] Add dynamic VRAM capacity detection and `VLLM_ADMIN_SECRET` override tests in `tests/unit/test_config_manager.py`
- [x] T008 [P] [US1] Add max context window limit enforcement and HTTP 400 Bad Request exception tests in `tests/unit/test_context_scaling_limits.py`

### Implementation for User Story 1

- [x] T009 [P] [US1] Correct `dev-rtx3060` RAM to 16GB and update network subnets (`10.0.0.0/8` for Platform A, `192.168.0.0/16` for Platform B & C) in `config/platform_profiles.json`
- [x] T010 [P] [US1] Remove static 11264MB VRAM default and expose `admin_secret` ("aiservice"), `api_key_enabled`, `api_keys` in `config/server_config.json`
- [x] T011 [US1] Implement dynamic VRAM binding and `VLLM_ADMIN_SECRET` environment variable override in `src/core/config_manager.py` (depends on T009, T010)
- [x] T012 [US1] Update subnet check logic and middleware handling for `10.0.0.0/8` and `192.168.0.0/16` in `src/core/network_detector.py` and `src/api/middleware/subnet_filter.py`
- [x] T013 [US1] Implement model context window scaling limits (2B/4B: 8K~16K, 9B/12B: 4K cap) in `src/core/llama_manager.py`
- [x] T014 [US1] Implement OpenAI-compatible 400 Bad Request context_length_exceeded error response and `POST /v1/admin/benchmark/run` endpoint in `src/api/server.py`
- [x] T015 [US1] Update VRAM benchmark result caching to `config/model_context_profiles.json` in `src/scripts/benchmark_context_scaling.py`
- [x] T016 [US1] Update `scripts/setup.sh` to run context scaling benchmark non-blocking with automatic fallback to `estimate_kv_cache_vram()`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final end-to-end verification and test suite execution

- [x] T017 [P] Execute quickstart validation scenarios defined in `specs/028-update-platform-network-profiles/quickstart.md`
- [x] T018 Run complete Pytest test suite (`uv run pytest`) to ensure 100% test pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - starts immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion.
- **Polish (Phase 4)**: Depends on User Story 1 completion.

### Within User Story 1

- Tests (T005-T008) can be written in parallel.
- Configuration file edits (T009-T010) can run in parallel.
- Config manager updates (T011) depend on T009 & T010.
- Network detector / middleware updates (T012) depend on T011.
- Llama manager context limits (T013) depend on T011.
- Server API 400 error handling (T014) depends on T013.
- Benchmark script caching (T015) can run alongside T013.
- Setup script integration (T016) depends on T015.

---

## Parallel Execution Examples: User Story 1

```bash
# 1. Run unit test tasks in parallel:
Task: "Add 16GB RAM and allowed subnets verification tests in tests/unit/test_config_manager_profiles.py"
Task: "Add CIDR subnet filtering tests for 10.0.0.0/8 and 192.168.0.0/16 in tests/unit/test_network_detector.py"
Task: "Add dynamic VRAM capacity detection and VLLM_ADMIN_SECRET override tests in tests/unit/test_config_manager.py"
Task: "Add max context window limit enforcement and HTTP 400 Bad Request exception tests in tests/unit/test_context_scaling_limits.py"

# 2. Run JSON config updates in parallel:
Task: "Correct dev-rtx3060 RAM to 16GB and update network subnets in config/platform_profiles.json"
Task: "Remove static 11264MB VRAM default and expose admin_secret in config/server_config.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (T005 - T016)
4. Validate with Phase 4 (T017, T018)
