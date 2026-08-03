# Implementation Plan: Service Platform Parity & Health Diagnostics Fix (`076-fix-service-platform-parity`)

**Feature Directory**: [`specs/076-fix-service-platform-parity`](file:///home/dev/storage/vllm_serv/specs/076-fix-service-platform-parity)  
**Spec**: [`spec.md`](spec.md)  

## Technical Context
- **Tech Stack**: Python 3.12, FastAPI, Uvicorn, httpx, Bash (UFW / iptables)
- **Target Files**:
  - `src/core/network_detector.py`: Active network interface detection and loopback IP mapping inspection
  - `scripts/diagnose_server_health.py`: Multi-loopback probing (`127.0.0.1`, `localhost`, `127.0.1.1`, active_ip) and HTML DOM keyword content verification
  - `start_server.sh`: Uvicorn 8082 dashboard launch via `uv run` with dual-port readiness check & atomic rollback
  - `scripts/setup.sh`: OS firewall ports (`8081/tcp`, `8082/tcp`) and global `chmod +x` enforcement
  - `status_server.sh`: Port 8082 LISTEN status and HTTP HTML content reporting

## Constitution Check
- **Article I (Language)**: All artifacts in Korean.
- **Article II/III (Zero-Mock & Real-Integration TDD)**: Tests must run against real sockets and HTTP responses.
- **Article VI (uv Environment)**: Run via `uv run python`.
- **Article VII (Mandatory Regression)**: Execute `uv run pytest`.

## Implementation Phases
- **Phase 0**: Research & technical decision consolidation (`research.md`)
- **Phase 1**: Entity model (`data-model.md`), contracts (`contracts/health-probe-contract.json`), validation guide (`quickstart.md`)
- **Phase 2**: Task breakdown generation via `/speckit-tasks`
