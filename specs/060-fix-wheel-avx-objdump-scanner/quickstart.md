# Quickstart & Verification Guide: 060-fix-wheel-avx-objdump-scanner

## Verification Scenarios

### Scenario 1: CLI 스캐너 직접 검증
```bash
uv run python scripts/verify_wheel_binary.py wheels/legacy_i7_930/llama_cpp_python-*.whl
```
- **Expected Outcome**:
  `✓ Wheel verified valid: CUDA enabled (... CPU .so files checked, ... CUDA device .so files validated, AVX clean: True)`
  Exit Code: 0

### Scenario 2: 전체 씨드 팩 마이그레이션 빌드 및 Post-Build 실측 검증
```bash
./scripts/make_seed_pack.sh --build-legacy
```
- **Expected Outcome**:
  `[SEED-PACK INFO] ✓ [POST-BUILD SUCCESS] 생성된 i7-930 휠 검증 통과 (AVX=0, CUDA=1).`
  `[SEED-PACK INFO] ✓ i7-930 사전 빌드 휠 디렉터리(wheels/legacy_i7_930) 아카이브 수록 검증 완료`
  Exit Code: 0

### Scenario 3: 단정 회귀 테스트 수트 실행
```bash
uv run pytest tests/unit/test_seed_pack.py
```
- **Expected Outcome**:
  13 passed, 1 skipped (100% Green Pass).
