# CLI Contract: `make_seed_pack.sh`

**Feature Branch**: `specs/019-seed-pack-generator`
**Date**: 2026-07-30

## Overview

`make_seed_pack.sh`는 `vllm_serv` 프로젝트의 핵심 소스코드, 설정, 쉘 스크립트만을 선택적으로 압축하여 타 GPU 서버 환경으로의 이관(Migration)을 위한 경량 Seed Pack 아카이브를 생성하는 CLI 쉘 스크립트입니다.

## Command Line Interface

```bash
./make_seed_pack.sh [OPTIONS]
# 또는
./scripts/make_seed_pack.sh [OPTIONS]
```

### Options

| Short Flag | Long Flag | Value / Type | Default | Description |
|---|---|---|---|---|
| `-o` | `--output` | `PATH` (string) | `dist/vllm_serv_seed.tar.gz` | 생성될 Seed Pack 아카이브 경로 지정 |
| | `--zip` | None (flag) | False | 기본 `.tar.gz` 대신 `.zip` 아카이브 포맷으로 생성 |
| `-h` | `--help` | None (flag) | False | 사용법 도움말 출력 후 종료 |

---

## Behavior & Execution Flow

1. **Working Directory Normalization**:
   - 스크립트의 실행 위치가 프로젝트 루트이거나 `scripts/` 디렉토리이거나 상관없이 `pyproject.toml`이 존재하는 프로젝트 루트 디렉토리로 `cd` 자동 이동.

2. **Output Directory Creation**:
   - 지정된 저장 경로의 부모 디렉토리(예: `dist/`)가 존재하지 않는 경우 `mkdir -p`로 자동 생성.

3. **Exclusion Guard Enforcement**:
   - `models/`, `.venv/`, `.bin/`, `logs/`, `build/`, `dist/`, `__pycache__/`, `.git/`, `*.tar.gz`, `*.zip`을 `--exclude` 인자로 강제 주입하여 압축 대상에서 하드웨어/모델 데이터를 무조건 제외.

4. **Root Link Generation**:
   - `scripts/make_seed_pack.sh` 생성 후 프로젝트 루트 `./make_seed_pack.sh`에 executable symbolic link 자동 생성 및 권한 설정(`chmod +x`).

---

## Exit Codes & Output Signals

| Exit Code | Meaning | Log Prefix | Trigger Conditions |
|---|---|---|---|
| `0` | Success | `[SEED-PACK INFO]` | Seed Pack 압축 파일 정상 생성 완료 |
| `1` | Error | `[SEED-PACK ERROR]` | `tar` / `zip` 실행 실패, 또는 필수 유틸리티 미설치 |

### Sample Output (Success)

```text
====================================================
▶ ⚡ vllm_serv Seed Pack 마이그레이션 아카이브 생성
====================================================
[SEED-PACK INFO] 프로젝트 루트 디렉토리: /home/dev/storage/vllm_serv
[SEED-PACK INFO] Seed Pack 압축 생성 중 (포맷: tar.gz)...
[SEED-PACK INFO] 대상 저장 경로: dist/vllm_serv_seed.tar.gz
[SEED-PACK INFO] 제외 디렉토리: models/, .venv/, .bin/, logs/, build/, __pycache__/
[SEED-PACK INFO] ✓ Seed Pack 생성 완료! (용량: 450 KB)
[SEED-PACK INFO] 타 시스템 마이그레이션 시 안내:
  1. target_server로 dist/vllm_serv_seed.tar.gz 복사
  2. tar -xzf vllm_serv_seed.tar.gz && cd vllm_serv
  3. ./setup.sh 실행 (가상환경 & CUDA llama.cpp 자동 구성)
  4. ./start_server.sh 실행 (모델 자동 받기 & 서빙 개설)
```
