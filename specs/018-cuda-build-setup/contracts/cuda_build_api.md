# Interface Contract: CUDA Build Pipeline & Verification API

## 1. CLI Setup Command Contract (`./setup.sh`)

- **Command**: `./setup.sh`
- **Pre-condition**: NVIDIA GPU, `nvidia-smi`, `/usr/bin/nvcc` CUDA Toolkit installed.
- **Behavior**:
  1. Validates project structure and prerequisites.
  2. Runs `uv sync` to sync virtual environment with `pyproject.toml`.
  3. Executes `CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python[server] --no-binary llama-cpp-python --force-reinstall`.
  4. Runs inline Python check: `uv run python -c "import llama_cpp; assert llama_cpp.llama_supports_gpu()"`
  5. Generates control scripts (`start_server.sh`, `status_server.sh`, `stop_server.sh`).
- **Post-condition**: `llama_supports_gpu()` returns `True`. Exit code `0`.
- **Failure Condition**: If `nvcc` is missing or CUDA compilation fails, exits immediately with code `1` and outputs `[SETUP ERROR]`.

---

## 2. Python Verification Contract (`src.core.process_manager`)

- **Method**: `ProcessManager.verify_and_build_llama_server() -> LlamaServerBinaryInfo`
- **Behavior**:
  - Checks for native C++ binary `llama-server` in `.bin/`.
  - If missing, checks `llama.cpp/CMakeLists.txt` and executes `cmake -B build -DGGML_CUDA=ON` and `cmake --build build --config Release -j`.
  - If source compilation is unavailable, falls back to `llama_cpp.server` python module, ensuring `llama_supports_gpu()` is `True`.

---

## 3. Real VRAM Monitoring Contract (`./status_server.sh`)

- **Behavior**:
  - Queries server process PID via `vllm_serv.pid` or `pgrep`.
  - Sends GET HTTP request to `/health/readiness`.
  - Executes `nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader`.
- **Expected Output**:
  - `프로세스 상태: 🟢 구동 중 (RUNNING, PID: <pid>)`
  - `/health/readiness` returns `{"status": "ready", "vram_offloaded_100pct": true}`.
  - `nvidia-smi` shows allocated VRAM > 2000MB and PID in process table (visible in `nvtop`).
