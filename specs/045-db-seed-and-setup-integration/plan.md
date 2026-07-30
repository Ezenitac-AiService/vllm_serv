# Implementation Plan: SQLite 메트릭 DB 시드 팩 및 서버 셋업 로직 연동 (045-db-seed-and-setup-integration)

**Branch**: `045-db-seed-and-setup-integration`  
**Specification**: [spec.md](file:///home/dev/storage/vllm_serv/specs/045-db-seed-and-setup-integration/spec.md)  
**Research**: [research.md](file:///home/dev/storage/vllm_serv/specs/045-db-seed-and-setup-integration/research.md)  
**Data Model**: [data-model.md](file:///home/dev/storage/vllm_serv/specs/045-db-seed-and-setup-integration/data-model.md)  

---

## Architecture & Implementation Overview

1. **Seed Script Creation (`scripts/seed_db.py`)**:
   - `data/metrics.db` 및 `config/server_config.json`에 초기 시드 키/로그 데이터 주입 로직 작성.
2. **Setup & Start Scripts Integration (`scripts/setup.sh`, `scripts/start_server.sh`)**:
   - `mkdir -p data` 및 `seed_db.py` 자동 호출 스텝 포함.
3. **Auto-seeding Fallback (`src/core/metrics_db.py`)**:
   - DB 파일 부재 시 자동으로 `seed_db.py`를 실행하여 부팅 시점 데이터 보장.
4. **Verification Test Suite**: `tests/unit/test_db_seed_integration.py`

---

## Constitution Compliance Check

- [x] Language: Korean primary for documentation, English for code.
- [x] Anti-Mock Enforcement: Real DB seeding & file execution tests.
- [x] All commands run with `uv run`.
