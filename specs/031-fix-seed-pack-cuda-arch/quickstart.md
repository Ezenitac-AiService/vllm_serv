# Quickstart Validation Guide: i7-930/GTX 1070 시드 팩 CMAKE 인자 및 Fast-Track 복원 검증 (031-fix-seed-pack-cuda-arch)

## 1. 개요 (Overview)

본 가이드는 `make_seed_pack.sh`에서 빌드한 `legacy-i7-930` 휠이 GTX 1070 타겟 장비에서 소스 컴파일 Fallback 없이 Fast-Track 검증을 100% 통과하는지 검증하는 시나리오입니다.

---

## 2. 사전 조건 (Prerequisites)

- `uv` 패키지 매니저 및 파이썬 3.12+ 가상환경
- NVIDIA CUDA Toolkit (`nvcc`) 설치 환경

---

## 3. 검증 시나리오 A: `make_seed_pack.sh` CMAKE 인자 검증 단위 테스트

### 명령어 실행

```bash
uv run pytest tests/unit/test_seed_pack_legacy.py
```

### 기대 결과 (Expected Outcome)

- `make_seed_pack.sh` 스크립트 내 `-DCMAKE_CUDA_ARCHITECTURES=61`, `-DGGML_NATIVE=OFF`, `FORCE_CMAKE=1` 수록 검증 테스트를 포함하여 8개 이상의 단위 테스트가 100% 통과 (`8 passed in < 5s`).

---

## 4. 검증 시나리오 B: 시드 팩 생성 및 `setup.sh` Fast-Track 통합 검증

### 명령어 실행

```bash
# 1. i7-930 휠 사전 컴파일 및 시드 팩 빌드
./scripts/make_seed_pack.sh --build-legacy

# 2. setup.sh 구동하여 Fast-Track 설치 및 GPU 가속 검증
./scripts/setup.sh
```

### 기대 결과 (Expected Outcome)

- `wheels/legacy_i7_930/llama_cpp_python*.whl` 휠이 성공적으로 사전 컴파일되어 번들링됨.
- `setup.sh` 실행 시 `[SETUP WARN] ⚠️ 사전 빌드 휠 복원 후 GPU 가속 검증 실패` 경고가 발생하지 않음.
- `✓ i7-930 사전 빌드 휠 Fast-Track 설치 및 CUDA GPU 가속 활성화 확인 완료 (C++ 소스 재컴파일 스킵됨)` 로그 출력과 함께 < 5초 이내에 휠 복원 완료.
