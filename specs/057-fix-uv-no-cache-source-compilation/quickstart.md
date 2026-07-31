# Quickstart & End-to-End Validation Guide: Tier 4 uv 휠 캐시 실측 검증 및 불일치 시 조건부 --no-cache-dir 파이프라인 (057-fix-uv-no-cache-source-compilation)

**Feature Branch**: `057-fix-uv-no-cache-source-compilation`  
**Created**: 2026-07-31  
**Spec Link**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/057-fix-uv-no-cache-source-compilation/spec.md)  
**Research Link**: [`research.md`](file:///home/dev/storage/vllm_serv/specs/057-fix-uv-no-cache-source-compilation/research.md)  
**Data Model Link**: [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/057-fix-uv-no-cache-source-compilation/data-model.md)  
**Contract Link**: [`contracts/fallback-pipeline-api.json`](file:///home/dev/storage/vllm_serv/specs/057-fix-uv-no-cache-source-compilation/contracts/fallback-pipeline-api.json)

---

## 🚀 Scenario 1: Seed Pack 생성 및 사전 휠 Post-Build 실측 검증

개발 머신에서 레거시 타겟 서비스 플랫폼(`legacy-i7-930-gtx1070`)용 사전 휠을 포함하는 Seed Pack을 안전하게 빌드하고 패키징하는 절차입니다.

```bash
# 1. 프로젝트 루트로 이동
cd /home/dev/storage/vllm_serv

# 2. make_seed_pack.sh 실행 (레거시 전용 휠 빌드 & 검증)
./scripts/make_seed_pack.sh --build-legacy

# 3. 기대 출력 및 결과 검증:
# - 기존 wheels/legacy_i7_930/*.whl 이 유효(AVX=0, CUDA=1)하면 즉시 재사용 "✓ Existing legacy wheel is valid"
# - 기존 휠 미존재/결함 시 --no-cache-dir 로 신규 빌드 후 Post-Build 3중 검증 수행
# - 검증 성공 시 vllm_serv_seed.tar.gz 아카이브 생성 완결
```

---

## 📦 Scenario 2: 타깃 머신 Seed Pack 압축 해제 (`unpack_seed.sh`) 및 유효 바이너리 보존 검증

서비스/개발/학습 타깃 머신에서 `vllm_serv_seed.tar.gz`의 압축을 풀 때, 기존에 설치되어 정상 작동 중인 CUDA 바이너리를 덮어쓰지 않고 안전하게 보존해 해제하는 절차입니다.

```bash
# 1. 프로젝트 루트에 vllm_serv_seed.tar.gz 및 unpack_seed.sh 배치 확인
cd /home/dev/storage/vllm_serv

# 2. unpack_seed.sh 실행 (또는 ./scripts/unpack_seed.sh)
./unpack_seed.sh vllm_serv_seed.tar.gz

# 3. 기대 출력 및 결과 검증:
# - 기존 .venv 또는 wheels/ 내 바이너리가 llama_supports_gpu_offload() 통과 시:
#   "ℹ️ [PRESERVED] 기존 정상 작동 바이너리를 보존하고 압축 해제를 진행합니다 (--skip-old-files)"
# - 기존 파일 권한 및 유효 바이너리가 100% 보존됨
```

---

## ⚡ Scenario 3: `setup.sh` Tier 4 조건부 uv 캐시 검증 및 `--no-cache-dir` 소스 재컴파일 파이프라인 검증

이관 타깃 서버에서 `./setup.sh` 실행 시, 기존 캐시 휠의 정상 작동 여부를 먼저 실측하고, CPU 전용일 때만 조건부로 캐시를 무효화하여 C++ 소스를 재컴파일하는 파이프라인 검증입니다.

```bash
# 1. 타깃 머신에서 setup.sh 실행
./setup.sh

# 2. 파이프라인 동작 시나리오 검증:
# Case A (정상 CUDA 캐시 휠 감지 시):
#   - uv pip install 후 실측 검증 통과 → 소스 재컴파일 스킵하고 수 초 만에 완결!
#
# Case B (오염된 CPU 전용 캐시 휠 감지 시):
#   - 1차 검증 실패 (AssertionError: GPU offload not supported)
#   - 로그 출력: "⚠️ [UV CACHE INVALID] uv 캐시 휠이 CPU 전용으로 감지되었습니다. 캐시 무효화(--no-cache-dir) 및 C++ 소스 재컴파일을 수행합니다..."
#   - uv pip uninstall llama-cpp-python 실행
#   - CMAKE_ARGS="-DGGML_CUDA=ON ..." uv pip install --no-cache-dir 구동
#   - C++ 소스 재컴파일 완결 후 실측 검증 PASS!

# 3. status_server.sh 구동 및 검증
./status_server.sh

# 기대 출력:
# llama-cpp-python GPU: ✓ CUDA 가속 활성
# Backend Process: PID 상주 확인
```

---

## 🧪 Scenario 4: 전체 단위 및 회귀 테스트 수트 실행

```bash
# 전체 회귀 테스트 실행 (헌법 VII조 의무 조항)
uv run pytest tests/unit/test_seed_pack.py
uv run pytest
```
