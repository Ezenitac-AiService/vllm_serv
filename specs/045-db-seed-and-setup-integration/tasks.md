# Tasks: SQLite 메트릭 DB 시드 팩 및 서버 셋업 로직 연동 (045-db-seed-and-setup-integration)

**Feature**: `045-db-seed-and-setup-integration`  
**Specification**: [spec.md](file:///home/dev/storage/vllm_serv/specs/045-db-seed-and-setup-integration/spec.md)  
**Implementation Plan**: [plan.md](file:///home/dev/storage/vllm_serv/specs/045-db-seed-and-setup-integration/plan.md)  

---

## Phase 1: Setup

- [x] T001 Verify project specification & planning files in `specs/045-db-seed-and-setup-integration/`

---

## Phase 2: Foundational (Core Infrastructure)

- [x] T002 Implement standalone CLI seed script in `scripts/seed_db.py` to populate seed API keys and 10 mock inference log records into `data/metrics.db`

---

## Phase 3: User Story 1 - 서버 셋업 및 초기 시작 시 SQLite DB 자동 생성 & 시드 팩 주입 (P1 🎯 MVP)

- [x] T003 [US1] Update `scripts/setup.sh` and `scripts/start_server.sh` to ensure `data/` directory creation and auto-trigger `seed_db.py` when DB is missing
- [x] T004 [US1] Add auto-seeding fallback trigger in `src/core/metrics_db.py` `MetricsDB.__init__()` when `data/metrics.db` does not exist

---

## Phase 4: User Story 2 - CLI DB Reset & Seed Script 지원 (P2)

- [x] T005 [P] [US2] Support `--reset` and `--force` CLI flags in `scripts/seed_db.py` for operator DB re-seeding

---

## Phase 5: Polish & Verification

- [x] T006 Create comprehensive unit & integration test suite in `tests/unit/test_db_seed_integration.py` and run `uv run pytest tests/unit/test_db_seed_integration.py -v`
