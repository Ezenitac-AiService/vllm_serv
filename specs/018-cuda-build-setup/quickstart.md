# Quickstart Validation Guide: Automated CUDA-Enabled llama.cpp Build & Setup Pipeline

## Prerequisites

- Operating System: Linux x86_64 (Ubuntu 22.04 LTS)
- GPU: NVIDIA GPU (e.g. GTX 1080 Ti with 11GB VRAM)
- Drivers & SDK: NVIDIA Display Driver, CUDA Toolkit (`/usr/bin/nvcc`), `cmake`, `ninja`
- Python Manager: `uv` 0.11+

---

## Runnable Verification Scenarios

### Scenario 1: `./setup.sh` 파이프라인 수행 및 CUDA GPU 지원 검증

1. **실행 명령어**:
   ```bash
   ./setup.sh
   ```
2. **GPU 가속 지원 검증**:
   ```bash
   uv run python -c "import llama_cpp; print('CUDA GPU Supported:', llama_cpp.llama_supports_gpu()); assert llama_cpp.llama_supports_gpu()"
   ```
3. **기대 결과**:
   - `CUDA GPU Supported: True` 출력 및 단동 Assertion 통과.

---

### Scenario 2: 서버 구동 및 nvtop / nvidia-smi VRAM 모니터링 검증

1. **서버 시작**:
   ```bash
   ./start_server.sh
   ```
2. **서버 상태 및 VRAM 모니터링 확인**:
   ```bash
   ./status_server.sh
   nvidia-smi
   ```
3. **기대 결과**:
   - `프로세스 상태: 🟢 구동 중 (RUNNING, PID: <pid>)`
   - `/health/readiness` ➔ `{"status": "ready", "vram_offloaded_100pct": true}`
   - `nvidia-smi` 및 `nvtop`에 `python` 또는 `llama-server` PID가 등록되고 사용 VRAM이 2,500MB 이상으로 시각화됨.

---

### Scenario 3: pytest 자동화 테스트 수트 100% 통과

1. **테스트 수트 실행**:
   ```bash
   uv run pytest -v
   ```
2. **기대 결과**:
   - 모든 단원/통합 테스트가 100% PASS.
