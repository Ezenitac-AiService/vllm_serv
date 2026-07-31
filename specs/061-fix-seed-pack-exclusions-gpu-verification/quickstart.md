# Quickstart & Verification Guide: 061-fix-seed-pack-exclusions-gpu-verification

## Verification Scenarios

### Scenario 1: 씨드 팩 아카이브 수록 제외 항목 검증
```bash
./scripts/make_seed_pack.sh --skip-legacy-build
tar -tzf dist/vllm_serv_seed.tar.gz | grep -E "^(specs/|\.agents/|\.specify/)"
```
- **Expected Outcome**:
  명령어 실행 결과가 0건(출력 없음). `tests/` 및 `src/` 등 필수 항목은 정상 수록됨.

### Scenario 2: 타겟 서버 `setup.sh` Fast-Track 5초 복원 검증
```bash
./scripts/setup.sh
```
- **Expected Outcome**:
  `[SETUP INFO] ✓ 사전 빌드 휠 Fast-Track 설치 및 CUDA GPU 가속 활성화 확인 완료 (C++ 소스 재컴파일 스킵됨)`
  `INSTALLED_VIA_FAST_TRACK=1` 확정 및 소스 재컴파일 파이프라인으로 유입되지 않음 (< 5초 완료).

### Scenario 3: 단정 회귀 테스트 수트 실행
```bash
uv run pytest tests/unit/test_seed_pack.py
```
- **Expected Outcome**:
  15 passed (100% Green Pass).
