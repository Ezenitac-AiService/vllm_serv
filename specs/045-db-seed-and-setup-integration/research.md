# Research & Technical Choices: 045-db-seed-and-setup-integration

## 1. Seed Script Design (`scripts/seed_db.py`)
- **Decision**: Python standalone script using `sqlite3` connecting to `data/metrics.db`.
- **Rationale**: Reuses native `MetricsDB` module without external dependencies, supports CLI `--reset` and `--force` options.
- **Alternatives Considered**: Raw SQL file import - discarded as python script allows dynamic timestamp generation (realistic recent dates).

## 2. Server Setup Integration (`scripts/setup.sh`)
- **Decision**: Add `mkdir -p data` and `uv run python scripts/seed_db.py` check during environment setup.
- **Rationale**: Guarantees database file and initial seed pack exist on new machine deployments.
