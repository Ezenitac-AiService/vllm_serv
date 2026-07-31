# CLI Contracts: Seed Pack Generation & Setup Fast-Track (029-prebuild-legacy-seed-pack)

## Contract 1: `scripts/make_seed_pack.sh` CLI Interface

### Usage
```bash
./scripts/make_seed_pack.sh [OPTIONS]
```

### Options
- `-o, --output PATH`: 생성할 아카이브 저장 경로 지정 (기본값: `dist/vllm_serv_seed.tar.gz`)
- `--zip`: `.tar.gz` 대신 `.zip` 포맷 생성
- `--build-legacy`: i7-930 전용 사전 컴파일 휠(`wheels/legacy_i7_930/*.whl`)을 명시적 CFLAGS/CMAKE_ARGS로 자동 컴파일 후 아카이브 수록 (기본 활성)
- `--skip-legacy-build`: i7-930 휠 사전 컴파일 건너뜀
- `-h, --help`: 도움말 출력

### Expected Log Output
```text
[SEED-PACK INFO] i7-930 전용 사전 컴파일 휠 패키지 빌드 시작...
[SEED-PACK INFO] CFLAGS="-march=x86-64" CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF"
[SEED-PACK INFO] ✓ i7-930 사전 빌드 휠 생성 완료: wheels/legacy_i7_930/llama_cpp_python-*.whl
[SEED-PACK INFO] ✓ Seed Pack 아카이브 수록 검증 완료 (wheels/legacy_i7_930/ 수록됨)
```

---

## Contract 2: `scripts/setup.sh` Fast-Track Wheel Installation Pipeline

### Behavior Contract for `legacy-i7-930-gtx1070` Platform
1. `setup.sh` 하드웨어 감지 파이프라인 수행.
2. `MATCHED_PROFILE`이 `legacy-i7-930-gtx1070`인 경우:
   - `wheels/legacy_i7_930/*.whl` 존재 시:
     ```text
     [SETUP INFO] ⚡ i7-930 타겟 플랫폼 감지! 사전 빌드 휠(wheels/legacy_i7_930/*.whl) Fast-Track 복원을 시작합니다.
     [SETUP INFO] C++ 소스 재컴파일을 건너뛰고 사전 빌드 휠을 가상환경(.venv)에 고속 설치합니다...
     ✓ llama-cpp-python 사전 빌드 휠 설치 완료 (3초 소요)
     ```
   - 휠 미존재 시:
     ```text
     [SETUP WARN] ⚠️ i7-930 사전 빌드 휠이 감지되지 않았습니다. 기존 소스 컴파일 파이프라인으로 Fallback합니다. (약 15~30분 소요 가능)
     ```
