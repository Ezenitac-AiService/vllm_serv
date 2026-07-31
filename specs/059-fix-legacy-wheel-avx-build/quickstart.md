# Quickstart & End-to-End Validation Guide: make_seed_pack.sh 레거시 사전 휠 Post-Build AVX 실측 검증 로직 및 빌드 플래그 정밀화 (059-fix-legacy-wheel-avx-build)

**Feature Branch**: `059-fix-legacy-wheel-avx-build`  
**Created**: 2026-07-31  
**Spec Link**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/059-fix-legacy-wheel-avx-build/spec.md)  
**Research Link**: [`research.md`](file:///home/dev/storage/vllm_serv/specs/059-fix-legacy-wheel-avx-build/research.md)  
**Data Model Link**: [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/059-fix-legacy-wheel-avx-build/data-model.md)  
**Contract Link**: [`contracts/wheel-verification-contract.json`](file:///home/dev/storage/vllm_serv/specs/059-fix-legacy-wheel-avx-build/contracts/wheel-verification-contract.json)

---

## 🚀 Scenario 1: `verify_wheel_binary.py` 독립 검증 시나리오

```bash
# 1. 프로젝트 루트로 이동
cd /home/dev/storage/vllm_serv

# 2. 레거시 i7-930 휠 검증 실행
uv run python scripts/verify_wheel_binary.py wheels/legacy_i7_930/llama_cpp_python-*.whl

# 3. 기대 출력 및 결과 검증:
# - Exit Code: 0
# - "✓ Wheel verified valid: CUDA enabled (... .so files checked, AVX clean: True)" 출력
# - CUDA GPU 라이브러리와 CPU 호스트 라이브러리가 명확히 구분 평가됨.
```

---

## 🚀 Scenario 2: `make_seed_pack.sh` 사전 휠 빌드 및 Post-Build 100% 통과 실측 시나리오

```bash
# 1. existing 휠 임시 삭제로 신규 컴파일 강제
rm -f wheels/legacy_i7_930/*.whl

# 2. make_seed_pack.sh 실행
./scripts/make_seed_pack.sh --build-legacy

# 3. 기대 출력 및 결과 검증:
# - "✓ [POST-BUILD SUCCESS] 생성된 i7-930 휠 검증 통과 (AVX=0, CUDA=1)." 출력
# - dist/vllm_serv_seed.tar.gz 아카이브 생성 완료
```

---

## 🧪 Scenario 3: 회귀 테스트 수트 구동

```bash
# 단위 및 회귀 테스트 수트 구동
uv run pytest tests/unit/test_seed_pack.py
```
