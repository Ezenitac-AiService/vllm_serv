# Quickstart & End-to-End Validation Guide: make_seed_pack.sh 빌드 백엔드 오류 해결 (058-fix-make-seed-pack-build-backend)

**Feature Branch**: `058-fix-make-seed-pack-build-backend`  
**Created**: 2026-07-31  
**Spec Link**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/058-fix-make-seed-pack-build-backend/spec.md)  
**Research Link**: [`research.md`](file:///home/dev/storage/vllm_serv/specs/058-fix-make-seed-pack-build-backend/research.md)  
**Data Model Link**: [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/058-fix-make-seed-pack-build-backend/data-model.md)  
**Contract Link**: [`contracts/build-backend-contract.json`](file:///home/dev/storage/vllm_serv/specs/058-fix-make-seed-pack-build-backend/contracts/build-backend-contract.json)

---

## 🚀 Scenario 1: `make_seed_pack.sh` 사전 휠 빌드 및 BackendUnavailable 0건 검증

```bash
# 1. 프로젝트 루트로 이동
cd /home/dev/storage/vllm_serv

# 2. 기존 휠 임시 삭제하여 신규 빌드 강제
rm -f wheels/legacy_i7_930/*.whl

# 3. make_seed_pack.sh 실행
./scripts/make_seed_pack.sh --build-legacy

# 4. 기대 출력 및 결과 검증:
# - "BackendUnavailable: Cannot import 'scikit_build_core.build'" 오류 0건!
# - "✓ [POST-BUILD SUCCESS] 생성된 i7-930 휠 검증 통과 (AVX=0, CUDA=1)." 출력
# - wheels/legacy_i7_930/*.whl 존재 확인
```

---

## 🧪 Scenario 2: 단위 테스트 수트 실행

```bash
# 단위 테스트 수트 구동
uv run pytest tests/unit/test_seed_pack.py
```
