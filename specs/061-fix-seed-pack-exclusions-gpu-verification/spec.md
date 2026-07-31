# Feature Specification: 씨드 팩 아카이브 `specs/` 제외 및 `setup.sh` 사전 빌드 휠 GPU 검증 동기화 격리 명세

**Feature ID**: `061-fix-seed-pack-exclusions-gpu-verification`  
**Created**: 2026-07-31  
**Status**: Draft / Analysis Complete  

---

## 1. Context & Root Cause Analysis (원인 분석)

### 1.1 현상 1: 씨드 팩 아카이브 내 개발 명세 디렉터리(`specs/`) 누출
- `scripts/make_seed_pack.sh`가 `dist/vllm_serv_seed.tar.gz` 아카이브 생성 시 `--exclude` 옵션에 `specs/` 디렉터리가 누락되어 불필요한 개발용 명세 아티팩트(`specs/*`)가 포함됨.

### 1.2 현상 2: 타겟 머신 `setup.sh` 실행 시 사전 빌드 CUDA 휠 Fast-Track 검증 실패 및 소스 재컴파일 Fallback 발생
사용자가 사전 빌드 휠이 번들링된 씨드 팩을 타겟 서버에 압축 해제 후 `./setup.sh`를 실행할 때, 다음과 같은 오류가 발생하며 Fast-Track 복원에 실패하고 소스 재컴파일로 Fallback됨:
```text
[SETUP INFO] ⚡ 사전 빌드 휠(wheels/legacy_i7_930/llama_cpp_python-0.3.34-py3-none-linux_x86_64.whl) Fast-Track 복원을 시작합니다...
[SETUP INFO] C++ 소스 재컴파일을 건너뛰고 사전 빌드 휠을 가상환경(.venv)에 고속 설치합니다...
...
[SETUP INFO] CUDA GPU 가속 지원 검증 중 (llama_supports_gpu_offload())...
[SETUP WARN] ⚠️ [FAST-TRACK FAIL] 사전 빌드 휠 복원 후 GPU 가속 검증 실패: GPU_OFFLOAD_FALSE (llama_supports_gpu_offload() 반환값 False)
[SETUP WARN] --- [FAST-TRACK FAIL TRACEBACK] ---
  Uninstalled 1 package in 3ms
  Installed 1 package in 5ms
  ERROR: llama_supports_gpu_offload() returned False
```

### 1.3 근본 원인 (Root Cause)
1. **`specs/` 제외 누락**: `make_seed_pack.sh`의 tar/zip 옵션에 `--exclude="specs"` 및 `-x "specs/*"` 항목이 지정되지 않음.
2. **`uv run` 자동 패키지 동기화(Auto-Sync) 덮어쓰기 오작동**:
   - `setup.sh`는 `uv pip install "$LEGACY_WHEEL"` 명령으로 사전 빌드된 CUDA 지원 `llama-cpp-python` 휠을 `.venv` 가상환경에 정상 설치함.
   - 하지만 직후 GPU 검증 단계에서 `uv run python -c "import llama_cpp..."` 명령을 실행함.
   - `uv run`은 `.venv` 상태와 `uv` 로컬 캐시/동기화 상태 간의 불일치를 감지하고, **스스로 `Uninstalled 1 package` / `Installed 1 package`를 실행하여 `.venv`에 설치된 CUDA 휠을 `uv` 캐시의 CPU 전용 휠로 원복 덮어쓰기(Overwrite)** 해버림 (`Uninstalled 1 package in 3ms / Installed 1 package in 5ms`).
   - 이에 따라 `llama_supports_gpu_offload()` 검증 시 이미 CPU 전용 패키지로 재설치된 상태여서 `False`를 리턴하고, Fast-Track이 실패하여 불필요한 소스 재컴파일 단계로 유입됨.

---

## 2. User Stories & Acceptance Scenarios

### User Story 1 (P1 - MVP): 씨드 팩 아카이브 경량화 (`specs/` exclusion)
As a system administrator deploying migration seed packs,  
I want `make_seed_pack.sh` to strictly exclude `specs/` directory from `dist/vllm_serv_seed.tar.gz` and zip archives,  
So that production migration archives contain only runtime application code and prebuilt wheels without raw dev specs.

- **Acceptance Scenario 1.1**:
  - Given `make_seed_pack.sh` creates `dist/vllm_serv_seed.tar.gz`,
  - When inspecting the tarball contents with `tar -tzf`,
  - Then no paths under `specs/` are included.

---

### User Story 2 (P1 - MVP): `setup.sh` Fast-Track GPU 검증 파이프라인 격리 (`.venv/bin/python` 사용)
As a target server operator running `./setup.sh`,  
I want `setup.sh` to execute python verification scripts directly via `.venv/bin/python` (or `uv run --no-sync`),  
So that `uv`'s auto-sync mechanism does not silently overwrite the newly restored prebuilt CUDA wheel in `.venv` with CPU-only packages, allowing Fast-Track restoration to complete in < 5 seconds.

- **Acceptance Scenario 2.1**:
  - Given a target machine with NVIDIA GPU and CUDA driver,
  - When `./setup.sh` installs the prebuilt legacy CUDA wheel from `wheels/legacy_i7_930/llama_cpp_python-*.whl`,
  - Then `.venv/bin/python` executes `llama_supports_gpu_offload()` check directly without triggering `uv` auto-sync or package re-installation,
  - And outputs `✓ 사전 빌드 휠 Fast-Track 설치 및 CUDA GPU 가속 활성화 확인 완료 (C++ 소스 재컴파일 스킵됨)` with `INSTALLED_VIA_FAST_TRACK=1`.

---

## Clarifications

### Session 2026-07-31
- Q: 씨드 팩 아카이브 제외 대상 확정 → A: Option B (`specs`, `.agents`, `.specify` 3개 디렉터리 제외, `tests` 폴더는 타겟 서버 현지 검증용으로 유지)

---

## 3. Functional Requirements (기능 요구사항)

- **FR-001**: `scripts/make_seed_pack.sh`의 tar 아카이브 생성 커맨드에 `--exclude="specs" --exclude=".agents" --exclude=".specify"`를 추가하고, zip 아카이브 생성 커맨드에 `-x "specs/*" -x ".agents/*" -x ".specify/*"` 항목을 추가해야 함 (`tests/` 디렉터리는 타겟 서버 현지 검증용으로 수록 보존).
- **FR-002**: `scripts/setup.sh` 내 Tier 1, Tier 2, Tier 3, Tier 4의 파이썬 기반 GPU 가속 검증 및 프로파일 감지 구문에서 `uv run python` 호출을 `.venv/bin/python` (또는 `$VENV_PYTHON`) 직접 실행 구문으로 교체하여 `uv` 패키지 자동 동기화 덮어쓰기 동작을 완전 차단해야 함.
- **FR-003**: `scripts/setup.sh` 실행 시 Fast-Track 사전 빌드 휠 복원 후 `llama_supports_gpu_offload()` 검증이 `True`를 반환하고, 소스 재컴파일 스킵(`INSTALLED_VIA_FAST_TRACK=1`)을 확정해야 함.
- **FR-004**: `tests/unit/test_seed_pack.py` 수트에 씨드 팩 아카이브 제외 항목 검증(`specs`, `.agents`, `.specify` 제외 및 `tests` 유지 확인) 및 `setup.sh` 파이썬 실행기 격리 단정 테스트를 수록해야 함.

---

## 4. Success Criteria (성공 기준)

- **SC-001**: `./scripts/make_seed_pack.sh --skip-legacy-build` 실행 후 `tar -tzf dist/vllm_serv_seed.tar.gz | grep "specs/"` 결과가 0건임.
- **SC-002**: `wheels/legacy_i7_930/` 사전 빌드 휠이 존재하는 상태에서 `./setup.sh` 실행 시 `✓ 사전 빌드 휠 Fast-Track 설치 및 CUDA GPU 가속 활성화 확인 완료` 출력과 함께 5초 이내 완료됨 (소스 재컴파일 스킵).
- **SC-003**: `uv run pytest tests/unit/test_seed_pack.py` 실행 시 100% Green Pass를 달성함.

---

## 5. Assumptions & Boundaries (가정 및 범위)

- **Assumptions**:
  - 타겟 서버 가상환경 경로는 `.venv/`에 위치함 (`.venv/bin/python` 존재).
  - 사전 빌드 휠(`llama_cpp_python-0.3.34-py3-none-linux_x86_64.whl`) 자체는 정상 CUDA 지원 휠임.
- **Boundaries**:
  - 本 명세는 씨드 팩 아카이브 포함 항목과 `setup.sh` Fast-Track 패키지 동기화 격리에 한정되며, 하드웨어 호환성 판단 기준 자체를 변경하지 않음.
