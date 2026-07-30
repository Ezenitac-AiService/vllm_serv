# Phase 0: Research & Design Decisions - 운영 쉘 스크립트 멀티 플랫폼 고도화

**Feature Branch**: `021-enhance-shell-scripts`
**Created**: 2026-07-30

## Research Tasks & Findings

### 1. `cpu_detector.py` 프로필 매칭 CLI (`--match-profile`) 설계

- **Decision**: `src/core/cpu_detector.py`에 `--match-profile` CLI 옵션과 `match_platform_profile()` 함수를 구현한다.
- **Rationale**:
  - 쉘 스크립트(`status_server.sh`, `setup.sh`, `start_server.sh`)에서 복잡한 파이썬 JSON 파싱/조건 비교 로직을 직접 구현하는 것은 유지보수성과 테스트 용이성을 저해함.
  - `config_manager.get_platform_profiles()`에서 프로필 정의 목록을 조회하고, `detect_system_hardware()`에서 수집된 SIMD 지원 여부, GPU Compute Capability (`sm_61`, `sm_86` 등), VRAM 크기를 바탕으로 최적의 프로필 ID를 반환함.
- **Alternatives Considered**:
  - 쉘 인라인 파이썬(`python -c "..."`): 코드 중복이 발생하고 단위 테스트 작성이 어려워 기각함.

### 2. `start_server.sh` 사전 점검(Pre-flight check) 및 Fail-Fast 정책

- **Decision**: 데몬 프로세스를 구동하기 직전, 하드웨어 가속 검증 스크립트 실행 및 결과 반환.
- **Rationale**:
  - CUDA GPU 미인식 또는 `nvcc` 미설치 시 백그라운드 데몬으로 전환한 후 비정상 종료되면 운영자가 에러 원인을 즉시 알아차리기 어려움.
  - 사전 점검 단계에서 `nvidia-smi` 및 `nvcc` 존재 여부, `llama-cpp-python` CUDA 빌드 상태를 검증하고, 실패 시 구체적 가이드(드라이버 점검, NVCC 패스 설정 등)와 함께 exit 1로 중단하여 안전한 fail-fast 정책 준수.
- **Alternatives Considered**:
  - 경고만 출력하고 백그라운드 구동 강행: 비정상 데몬 프로세스가 방치될 수 있어 헌장 원칙에 따라 기각함.

### 3. `status_server.sh` 터미널 리포트 포맷팅

- **Decision**: `uv run python -m src.core.cpu_detector --report` 결과를 기존 서빙 프로세스/포트/VRAM 정보 상단에 깔끔한 헤더와 함께 출력.
- **Rationale**:
  - 기존 프로세스 PID, 포트 점유, VRAM 사용률 출력에 더해 현재 가동 하드웨어의 CPU SIMD 지원(SSE4.2/AVX/AVX2/F16C/FMA), GPU Compute Capability, 매칭 프로필을 종합해서 보여줌으로써 멀티 플랫폼 운영 투명성 확보.

### 4. `make_seed_pack.sh` 멀티 플랫폼 파일 패키징 및 이관 가이드

- **Decision**: `make_seed_pack.sh` 파일 목록 검증 로직에 `config/platform_profiles.json`을 명시적으로 수록하고, 압축 완료 후 타겟 머신(예: 레거시 i7 930 서버)에서의 `./setup.sh` 구동 가이드를 출력함.
- **Rationale**:
  - 타 서버 이관 시 멀티 플랫폼 프로필 정의가 누락되면 타겟 머신에서 올바른 CMAKE_ARGS 감지가 불가능하므로 패키징 검증 필수.
