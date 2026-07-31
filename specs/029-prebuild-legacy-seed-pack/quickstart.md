# Quickstart Validation Guide (029-prebuild-legacy-seed-pack)

본 가이드는 `make_seed_pack.sh`를 사용한 i7-930 전용 휠 번들링 및 `setup.sh` Fast-Track 고속 복원 검증 절차를 설명합니다.

## Prerequisites

- Python 3.11+ 및 `uv` 환경
- 레포지토리 루트: `/home/dev/storage/vllm_serv`

---

## 1. i7-930 사전 빌드 휠 포함 시드 팩 생성 검증

```bash
# 1. 시드 팩 생성 (i7-930 전용 사전 컴파일 휠 자동 번들링)
./scripts/make_seed_pack.sh

# 2. 생성된 시드 팩 내 wheels/legacy_i7_930/ 수록 여부 검증
tar -tzf dist/vllm_serv_seed.tar.gz | grep "wheels/legacy_i7_930"
```

**Expected Outcome**: `wheels/legacy_i7_930/llama_cpp_python-*.whl` 파일 목록이 정상 출력됨.

---

## 2. i7-930 Fast-Track 고속 복원 및 setup.sh 검증

```bash
# 1. 시드 팩 테스트 아카이브 해제
mkdir -p /tmp/test_seed && tar -xzf dist/vllm_serv_seed.tar.gz -C /tmp/test_seed
cd /tmp/test_seed

# 2. i7-930 모의 프로필로 setup.sh 실행 검증
./scripts/setup.sh
```

**Expected Outcome**:
- i7-930 환경 감지 시 C++ 소스 재컴파일을 건너뛰고 사전 빌드 휠이 `uv pip install`로 3초 내 고속 주입됨.
- 전체 구축 시간이 3분 이내로 완수됨.

---

## 3. Pytest 테스트 수트 실행

```bash
uv run pytest tests/unit/test_shell_scripts.py -v
uv run pytest
```
