# Quickstart & Real Verification Guide: Seed Pack & setup.sh Sync (054-seedpack-setup-sync)

**Feature Branch**: `054-seedpack-setup-sync`
**Date**: 2026-07-31

---

## Quickstart Verification Steps

본 검증 가이드는 신규 스펙(임베딩/리랭커 포트 8090, 8091 및 핵심 모듈)이 `setup.sh`, `make_seed_pack.sh`, `seed_db.py`에 올바르게 반영되었는지 실측 검증하는 절차를 안내합니다.

---

### Step 1: `setup.sh` 방화벽 포트 4종 및 필수 파일 검증

1. 아래 명령어로 `setup.sh` 실행 및 방화벽 포트 설정 확인:

```bash
bash scripts/setup.sh
```

2. 생성된 `scripts/configure_firewall.sh` 및 스크립트 출력에서 4개 포트가 포함되었는지 확인:

```bash
grep "PORTS=" scripts/configure_firewall.sh
```

**기대 출력**:
```text
PORTS=(8081 8089 8090 8091)
```

---

### Step 2: Seed Pack 생성 및 아카이브 검증 (`make_seed_pack.sh`)

1. 아래 명령어로 Seed Pack 패키징 수행:

```bash
bash scripts/make_seed_pack.sh
```

2. 생성된 아카이브(`dist/vllm_serv_seed.tar.gz`) 내 `auxiliary_manager.py` 및 카탈로그 파일 존재 확인:

```bash
tar -tzf dist/vllm_serv_seed.tar.gz | grep "auxiliary_manager.py"
```

**기대 출력**:
```text
./src/core/auxiliary_manager.py
```

---

### Step 3: SQLite DB 시드 주입 및 엔드포인트 수록 검증 (`seed_db.py`)

1. 시드 DB 주입 스크립트 실행:

```bash
uv run python scripts/seed_db.py --reset
```

2. SQLite DB에서 `/v1/embeddings` 및 `/v1/rerank` 레코드 등록 확인:

```bash
uv run python -c "import sqlite3; conn=sqlite3.connect('data/metrics.db'); print(conn.execute('SELECT DISTINCT endpoint FROM metrics').fetchall())"
```

**기대 출력**:
```text
[('/v1/chat/completions',), ('/v1/embeddings',), ('/v1/rerank',)]
```

---

### Step 4: 전체 회귀 및 동기화 테스트 실행

```bash
uv run pytest tests/unit/test_seed_pack_sync.py tests/unit/test_seed_pack.py tests/integration/test_migration_pipeline.py
```

**기대 출력**:
```text
======================== 100% passed in X.XXs ========================
```
