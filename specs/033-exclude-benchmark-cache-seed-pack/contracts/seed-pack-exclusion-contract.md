# Seed Pack Exclusion Contract: 아카이브 필터링 표준 규격 (033-exclude-benchmark-cache-seed-pack)

## 1. CLI Execution Contract

`scripts/make_seed_pack.sh` 실행 결과 생성되는 시드 팩 아카이브(`dist/vllm_serv_seed.tar.gz`)는 다음 계약 검증(Contract Assertion) 조건을 만족해야 합니다.

### Mandatory Included Files (MUST Exist)
- `config/model_catalog.json`
- `config/platform_profiles.json`
- `config/server_config.json`
- `scripts/setup.sh`
- `src/api/server.py`
- `wheels/legacy_i7_930/`

### Mandatory Excluded Files (MUST NOT Exist)
- `config/model_context_profiles.json`
- `.legacy/`
- `benchmark_results.json`
- `*.jsonl`
- `models/`
- `.venv/`
