# Quickstart Validation Guide: Seed Pack Archiver & Migration Pipeline

**Feature Branch**: `specs/019-seed-pack-generator`
**Date**: 2026-07-30

## Overview

본 가이드는 `make_seed_pack.sh`를 구동하여 Seed Pack을 생성하고, 독립된 임시 테스트 환경에서 압축을 풀어 타 서버 마이그레이션 파이프라인 (`./setup.sh` -> `./start_server.sh`)을 검증하는 실행 절차를 규정합니다.

---

## Scenario 1: Local Seed Pack Generation Verification

### Command

```bash
# 프로젝트 루트에서 실행
./make_seed_pack.sh
```

### Expected Output

1. `dist/vllm_serv_seed.tar.gz` 파일 생성 완료.
2. 파일 용량이 10MB 미만 (약 300KB ~ 1MB 수준).
3. 터미널 출력에 생성 정보 및 타 시스템 이관 안내 메시지 출력.

---

## Scenario 2: Zip Format Generation Verification

### Command

```bash
./make_seed_pack.sh --zip -o dist/custom_seed.zip
```

### Expected Output

1. `dist/custom_seed.zip` 파일 정상 생성.
2. `unzip -l dist/custom_seed.zip` 수행 시 `models/`, `.venv/`, `.bin/` 제외 확인.

---

## Scenario 3: End-to-End Migration Simulation in Temporary Sandbox

### Step 1: Create Sandbox Environment

```bash
# 프로젝트 소스로부터 Seed Pack 생성
./make_seed_pack.sh -o /tmp/sandbox_seed.tar.gz

# 독립 임시 디렉토리 생성 및 압축 해제
mkdir -p /tmp/vllm_migrated_sandbox
cd /tmp/vllm_migrated_sandbox
tar -xzf /tmp/sandbox_seed.tar.gz
```

### Step 2: Restore Virtualenv & CUDA Build

```bash
# 복원된 디렉토리에서 setup.sh 실행
./setup.sh
```

### Expected Outcome
- `uv` 설치 및 `uv sync` 성공.
- `nvcc` 및 NVIDIA GPU 감지.
- CUDA 가속 `llama-cpp-python` 설치 성공.
- `uv run python -c "import llama_cpp; assert llama_cpp.llama_supports_gpu()"` 정상 검증 (`True`).

---

## Scenario 4: Automated Pytest Suite Execution

```bash
# 전체 테스트 수트 실행
uv run pytest tests/unit/test_seed_pack.py -v
```

### Expected Outcome
- 100% 테스트 통과 (`PASSED`).
