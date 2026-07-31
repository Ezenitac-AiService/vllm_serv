# Quickstart & Verification: 045-db-seed-and-setup-integration

## Runnable Validation Commands

### 1. Execute DB Seeding CLI Script
```bash
uv run python scripts/seed_db.py --reset
```

### 2. Verify Unit Test Suite
```bash
uv run pytest tests/unit/test_db_seed_integration.py -v
```

### 3. Verify Setup Script Integration
```bash
rm -rf data/metrics.db
bash scripts/setup.sh
```
