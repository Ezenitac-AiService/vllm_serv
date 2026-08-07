# Quickstart Validation Guide: Seed Pack 복원 스크립트 (`unpack_seed.sh`)

**Feature Directory**: `specs/111-unpack-seed-script-enhancement`

---

## Validation Scenarios

### Scenario 1: POSIX Tarball (.tar.gz) 비파괴 복원 검증
```bash
# 1. 시드 팩 아카이브 생성
./scripts/make_seed_pack.sh -o dist/test_seed.tar.gz

# 2. 타겟 디렉터리로 비파괴 복원 실행
./scripts/unpack_seed.sh -i dist/test_seed.tar.gz -t /tmp/unpack_test_targz

# 3. 필수 구성 파일 복원 검증
test -f /tmp/unpack_test_targz/config/platform_profiles.json
test -f /tmp/unpack_test_targz/scripts/start_server.sh
```

### Scenario 2: ZIP (.zip) 아카이브 사전 검증 및 복원
```bash
# 1. ZIP 시드 팩 생성
./scripts/make_seed_pack.sh --zip -o dist/test_seed.zip

# 2. 사전 무결성 검증만 수행 (--verify-only)
./scripts/unpack_seed.sh -i dist/test_seed.zip --verify-only

# 3. 비파괴 압축 해제 실행
./scripts/unpack_seed.sh -i dist/test_seed.zip -t /tmp/unpack_test_zip
```

### Scenario 3: 단위 및 회귀 테스트 수트 검증
```bash
uv run pytest tests/unit/test_shell_scripts.py
```
