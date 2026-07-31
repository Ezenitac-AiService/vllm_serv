# Tasks: 시드 팩 마이그레이션 및 setup.sh 관리자 권한·방화벽 자동화 (039-seed-pack-sudo-firewall-migration)

**Input**: Design documents from `/specs/039-seed-pack-sudo-firewall-migration/`  
**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/039-seed-pack-sudo-firewall-migration/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/039-seed-pack-sudo-firewall-migration/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/039-seed-pack-sudo-firewall-migration/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/039-seed-pack-sudo-firewall-migration/data-model.md), [contracts/](file:///home/dev/storage/vllm_serv/specs/039-seed-pack-sudo-firewall-migration/contracts/)

**Tests**: 실체적 테스트 필수 (Constitution v1.3.1 - Anti-Mock Discipline)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and specification structure verification

- [x] T001 Verify specification structure and contract alignments in `specs/039-seed-pack-sudo-firewall-migration/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core script templates and Python data structure extensions that MUST be ready before user story implementation

**⚠️ CRITICAL**: Foundational tasks must be completed before implementing user stories

- [x] T002 [P] Create `scripts/configure_firewall.sh` template script header with error handling in `scripts/configure_firewall.sh`
- [x] T003 [P] Extend `FirewallStatusInfo` dataclass and firewall system types in `src/core/firewall_manager.py`

**Checkpoint**: Core foundational data structures and script templates ready.

---

## Phase 3: User Story 1 - sudo 관리자 권한 승격 및 유지·소유권 보정 (Priority: P1) 🎯 MVP

**Goal**: `setup.sh` 실행 최전단 대화형 `sudo -v` 승격, 백그라운드 타임스탬프 갱신 데몬 유지, 비대화형 환경 복구 헬퍼 생성, `sudo ./setup.sh` 실행 완료 후 `$SUDO_USER` 계정 소유권 자동 환원 (`chown -R`)

**Independent Test**: 일반 사용자 계정에서 `setup.sh` 구동 시 최전단 `sudo -v` 승격 후 백그라운드 타임스탬프 갱신 데몬 구동 및 `sudo ./setup.sh` 실행 시 `.venv`, `logs`, `config` 소유권 자동 보정 실측 검증

### Tests for User Story 1 (Constitution v1.3.1 Real Verification)

- [x] T004 [P] [US1] Create unit test for sudo keepalive daemon trap and TTY detection in `tests/unit/test_shell_scripts.py`
- [x] T005 [P] [US1] Create unit test for ownership correction logic (`SUDO_USER` detection and `chown`) in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement TTY check, `sudo -v` interactive elevation, and background keepalive daemon (`while true; do sudo -n true; sleep 50; done &`) with trap signal handler in `scripts/setup.sh`
- [x] T007 [US1] Implement non-interactive sudo restriction check and warning banner output with `scripts/configure_firewall.sh` auto-generation in `scripts/setup.sh`
- [x] T008 [US1] Implement `$SUDO_USER` detection and automatic ownership remediation (`chown -R "$SUDO_USER:$SUDO_USER"`) for `.venv`, `logs`, `config` in `scripts/setup.sh`

**Checkpoint**: User Story 1 fully functional and testable independently (MVP ready).

---

## Phase 4: User Story 2 - 멀티 OS 방화벽 감지 및 포트 개방 자동화·시드 팩 번들링 (Priority: P2)

**Goal**: 타겟 서버 Linux OS 방화벽(`ufw`, `firewalld`, `nftables`, `iptables`) 자동 감지 및 서비스 포트(`8081/tcp`, `8089/tcp`) 개방 지원, 시드 팩 압축 포함 및 실체적 테스트 통과

**Independent Test**: `ufw` 또는 `firewalld` 활성화 서버에서 `setup.sh` 및 `configure_firewall.sh` 실행 후 `8081/tcp`, `8089/tcp` 포트 룰셋 반영 및 physical host 소켓 프로브 실측 검증

### Tests for User Story 2 (Constitution v1.3.1 Anti-Mock Tests)

- [x] T009 [P] [US2] Create non-mocked real OS firewall state inspection test in `tests/unit/test_firewall_manager_real.py`
- [x] T010 [P] [US2] Create shell script syntax and firewall port opening validation tests in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 2

- [x] T011 [P] [US2] Implement multi-OS firewall detection (`ufw`, `firewalld`, `nftables`, `iptables`) and rule application in `scripts/configure_firewall.sh`
- [x] T012 [US2] Implement `generate_fallback_script` method and multi-OS firewall support (`firewalld`, `nftables`, `iptables`) in `src/core/firewall_manager.py`
- [x] T013 [US2] Integrate multi-OS firewall detection logic and port opening call (`8081`, `8089`) into `scripts/setup.sh`
- [x] T014 [US2] Update seed pack bundler script to include `configure_firewall.sh` and updated modules in `scripts/make_seed_pack.sh`

**Checkpoint**: User Stories 1 AND 2 fully functional and independently testable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates, full quickstart validation, and regression test suite execution

- [x] T015 [P] Update documentation in `README.md` for seed pack sudo elevation and multi-OS firewall setup options
- [x] T016 Execute end-to-end quickstart validation scenarios defined in `specs/039-seed-pack-sudo-firewall-migration/quickstart.md`
- [x] T017 Run complete pytest suite with `uv run pytest` to ensure zero regressions across unit and real-execution tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) and User Story 2 (P2) can proceed sequentially (US1 → US2) or in parallel if staffed
- **Polish (Phase 5)**: Depends on User Story 1 and User Story 2 completion

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Starts after Foundational (Phase 2) - Independently testable

### Parallel Opportunities

- T002 and T003 can run in parallel (Foundational)
- Test writing T004 and T005 can run in parallel (User Story 1)
- Test writing T009, T010, and implementation T011 can run in parallel (User Story 2)
- T015 documentation can run in parallel during Polish phase

---

## Parallel Example: User Story 1

```bash
# Launch test creation in parallel:
Task: "Create unit test for sudo keepalive daemon trap and TTY detection in tests/unit/test_shell_scripts.py"
Task: "Create unit test for ownership correction logic (SUDO_USER detection and chown) in tests/unit/test_shell_scripts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Sudo elevation & ownership remediation)
4. **STOP and VALIDATE**: Verify User Story 1 interactive & non-interactive behaviors
5. Deliver MVP

### Incremental Delivery

1. Setup + Foundational -> Infrastructure ready
2. Add User Story 1 -> Test independently -> Deliver MVP
3. Add User Story 2 -> Test multi-OS firewall & seed pack -> Deliver full feature
4. Run Polish phase validation
