# Phase 1 Data Model: `llama-server` 네이티브 바이너리 경로 바인딩 (`081-fix-reranker-binary-path-resolution`)

## Data Models & Data Structures

### 1. LlamaServerBinaryInfo (바이너리 식별 구조체)

`src/core/process_manager.py` 클래스 내부 데이터 구조:

| 필드명 | 타입 | 설명 |
|-------|------|------|
| `binary_path` | `str` | 감지된 네이티브 `llama-server` 바이너리 절대 경로 (예: `/usr/local/lib/ollama/llama-server`) |
| `is_cuda_enabled` | `bool` | GPU/CUDA 가속 여부 (`True`) |
| `build_source` | `str` | 바이너리 탐지 출처 (`PATH`, `LOCAL_BIN`, `CMAKE_BUILD`, `PYTHON_MODULE_FALLBACK`) |

### 2. Binary Path Resolution Priority List

`ProcessManager.verify_and_build_llama_server()` 경로 탐색 순서:

1. `llama-server` (shutil.which)
2. `llama-cpp-server` (shutil.which)
3. `/usr/local/lib/ollama/llama-server` (OS 파일 존재 및 실행 권한 체크)
4. `/opt/ollama/lib/ollama/llama-server` (OS 파일 존재 및 실행 권한 체크)
5. `/usr/local/bin/llama-server` (OS 파일 존재 및 실행 권한 체크)
6. `/usr/bin/llama-server` (OS 파일 존재 및 실행 권한 체크)
7. `.bin/llama-server` (로컬 컴파일 저장소)
8. `llama.cpp/build/bin/llama-server` (소스 컴파일 저장소)
9. `PYTHON_MODULE_FALLBACK` (`sys.executable -m llama_cpp.server`)
