# Quickstart & Verification Guide: Fix setup.sh Port Sourcing

**Feature ID**: 096-fix-setup-port-sourcing  

## 1. Quick Verification Scenario

Run `./setup.sh --skip-benchmark` from root to confirm clean execution:

```bash
./setup.sh --skip-benchmark
```

### Expected Output
- Step 3 outputs `[INFO] 서빙 포트 설정: 8081/tcp ...`
- Zero `line 437: get_configured_port: command not found` errors.
- Exit code: 0.

## 2. Unit Test Verification

```bash
uv run pytest tests/unit/test_setup_benchmark_integration.py -v
```
