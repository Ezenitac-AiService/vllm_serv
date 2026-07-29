# Research: Automated CUDA-Enabled llama.cpp Build & Setup Pipeline

## Research Objectives

1. **`setup.sh` CUDA 빌드 강형화 (CUDA Wheel & CMAKE_ARGS)**:
   - `uv sync` 수행 시 PyPI의 CPU 전용 prebuilt 휠(`llama_cpp_python`) 대신 CUDA 가속 확장 모듈이 엮이도록 보장하는 최적의 환경변수 및 의존성 주입 방식 확립.
2. **`pyproject.toml` 의존성 보존 (uv sync Persistence)**:
   - `uv sync` 실행 시 CUDA 컴파일된 `llama-cpp-python[server]` 패키지가 언인스톨되지 않고 가상환경에 유지되도록 의존성 명시.
3. **`ProcessManager` C++ CMake CUDA 옵션 검증**:
   - `llama-server` 바이너리 소스 컴파일 시 `-DGGML_CUDA=ON` 플래그가 누락 없이 전달되도록 보장.
4. **CUDA 환경 누락 시 Fail-Fast 방어 정책**:
   - `nvcc` 또는 NVIDIA CUDA 드라이버 미존재 시 CPU 폴백을 차단하고 명확한 예외 메시지로 조기 중단.

---

## Research Findings & Architectural Decisions

### Decision 1: `setup.sh` 파이프라인 CUDA 가속 패키지 컴파일/설치 방식

- **Selected Approach**: `pyproject.toml`의 `dependencies`에 `"llama-cpp-python[server]>=0.3.0"`를 명시하고, `./setup.sh`에서 `uv sync` 전/후에 `CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python[server] --no-binary llama-cpp-python --force-reinstall`을 조합하여 CUDA 바인딩을 강제 빌드한다.
- **Rationale**:
  - standard `pip install llama-cpp-python`은 CPU 전용 prebuilt wheel을 설치하므로 `llama_supports_gpu()`가 `False`를 반환함.
  - `CMAKE_ARGS="-DGGML_CUDA=on"` 및 `--no-binary llama-cpp-python`을 지정하여 nvcc를 통해 CUDA 텐서 지원 공유 라이브러리(`libllama.so` with CUDA kernels)를 C++ 빌드하도록 만듦.
- **Alternatives Considered**:
  - PyPI prebuilt wheel 직접 수용: CPU 전용 휠이 다운로드되어 `nvtop` 및 VRAM 점유 불발 (기각).

---

### Decision 2: `pyproject.toml` 의존성 지속성 보장 (uv sync Persistence)

- **Selected Approach**: `pyproject.toml` [project.dependencies] 섹션에 `"llama-cpp-python[server]>=0.3.0"` 및 `"cmake>=3.28"`, `"ninja>=1.11"` 추가.
- **Rationale**:
  - `uv sync`는 `pyproject.toml`에 정의되지 않은 가상환경 내 패키지를 자동으로 언인스톨함.
  - `pyproject.toml`에 프로젝트 공식 의존성으로 등록해두면 `./setup.sh` 실행 중 `uv sync` 단계에서 `llama-cpp-python` 관련 패키지가 삭제되는 현상을 완전히 방지할 수 있음.

---

### Decision 3: `ProcessManager` C++ llama-server CMake CUDA 빌드 옵션

- **Selected Approach**: `ProcessManager.verify_and_build_llama_server()`에서 CMake 구동 시:
  ```python
  subprocess.run(["cmake", "-B", build_dir, "-DGGML_CUDA=ON"], cwd=llama_src_dir, check=True)
  subprocess.run(["cmake", "--build", build_dir, "--config", "Release", "-j"], cwd=llama_src_dir, check=True)
  ```
- **Rationale**:
  - C++ native `llama-server` 바이너리는 `-DGGML_CUDA=ON` 옵션을 명시적으로 전달해야 CUDA 연산 커널이 포함되어 컴파일됨.
  - 생성된 바이너리를 `.bin/llama-server`로 배치하면 Python wrapper overhead 없이 100% 네이티브 C++ CUDA 성능을 발휘함.

---

### Decision 4: CUDA 불가능 환경 조기 중단 (Fail-Fast Policy)

- **Selected Approach**: `setup.sh` 2단계(NVIDIA GPU 검증) 및 `ProcessManager` 구동 시 `shutil.which("nvcc")` 및 `nvidia-smi`를 검사하여 누락된 경우 즉시 종료 및 오류 출력:
  ```bash
  if ! command -v nvcc &> /dev/null; then
      echo -e "[SETUP ERROR] NVIDIA CUDA Toolkit (nvcc)가 감지되지 않았습니다."
      echo -e "NVIDIA GPU 가속 서빙을 위해 nvcc 및 CUDA SDK 설치가 필수입니다."
      exit 1
  fi
  ```
- **Rationale**:
  - 헌장(Constitution) 및 명세서(Spec)에 따라 CPU-only 롤백을 엄격히 금지함.
  - 조기 중단(Fail-Fast)을 통해 잘못된 CPU 휠 설치 및 가짜 200 OK 서빙을 원천 차단함.
