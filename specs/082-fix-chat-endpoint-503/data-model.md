# Phase 1 Data Model: Chat Endpoint 503 Fix & Llama Server Binary Resolution Refactoring

**Feature Branch**: `082-fix-chat-endpoint-503`

## 1. Core Entities & Data Structures

### LlamaServerBinaryInfo
`ProcessManager.verify_and_build_llama_server()`에서 반환하는 바이너리 탐지 결과 데이터 구조체.

| 필드명 (Field) | 타입 (Type) | 제약 조건 (Constraints) | 설명 (Description) |
|---|---|---|---|
| `binary_path` | `str` | absolute file path, executable | 검증된 C++ `llama-server` 바이너리 또는 Python 서빙 모듈 실행 경로 |
| `is_cuda_enabled` | `bool` | True / False | CUDA 하드웨어 가속 지원 여부 |
| `build_source` | `str` | Enum: `PATH`, `LOCAL_BIN`, `CMAKE_BUILD`, `SYSTEM_BIN`, `PYTHON_MODULE_FALLBACK` | 바이너리 탐지 및 빌드 출처 (OLLAMA_LIB 제외됨) |

---

## 2. Process Manager Binary Resolution Rules

```
[System Binary Candidates Scan]
        │
        ├── Candidate contains "/ollama/" or matches internal libs? ──► YES ──► DISCARD
        │
        └── NO ──► Test `[path, "--help"]` Execution 
                      │
                      ├── Failed / Timeout ──► DISCARD
                      │
                      └── Passed ──► Return LlamaServerBinaryInfo(build_source)
```

1. **Rule 1 (Ollama Filtering)**: `shutil.which` 또는 시스템 경로 탐지 시 `/ollama/` 서브스트링 포함 경로는 미검증 내부 라이브러리로 간주하여 무조건 제외.
2. **Rule 2 (Sanity Check)**: 후보 바이너리에 대해 실행 권한(`os.access(path, os.X_OK)`) 확인 및 `subprocess` 실행 테스트로 스탠드얼론 작동 여부 검증.
3. **Rule 3 (Fallback Cascade)**:
   - `PATH` 내 스탠드얼론 `llama-server`
   - `/usr/local/bin/llama-server` 또는 `/usr/bin/llama-server` (Ollama 제외)
   - `.bin/llama-server` (프로젝트 내부 빌드 바이너리)
   - `llama-cpp-python` 파이썬 모듈 폴백 (`PYTHON_MODULE_FALLBACK`)
