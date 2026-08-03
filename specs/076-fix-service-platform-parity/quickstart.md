# Quickstart & Validation Guide: `076-fix-service-platform-parity`

## Validation Steps on Service Platform

1. **Clean Seed Pack Packaging**:
   ```bash
   ./scripts/make_seed_pack.sh
   ```

2. **Deploy & Environment Setup on Target Service Platform**:
   ```bash
   tar -xzf vllm_serv_seed.tar.gz -C vllm_serv && cd vllm_serv
   ./setup.sh
   ```

3. **One-Stop Background Launch with Dual Readiness Verification**:
   ```bash
   ./start_server.sh
   ```

4. **Run Parity Diagnostics & DOM Content Verification**:
   ```bash
   uv run python scripts/diagnose_server_health.py
   ```

### Expected Output
- `Port 8081_llm_main: ✅ OPEN`
- `Port 8082_dashboard: ✅ OPEN`
- `/v1/models: ✅ 200 OK`
- `/health: ✅ 200 OK`
- `/v1/chat/completions: ✅ 200 OK`
- `🖥️ 웹 대시보드 E2E 렌더링 : ✅ ON`
- `STATUS: 🎉 SYSTEM HEALTHY`
