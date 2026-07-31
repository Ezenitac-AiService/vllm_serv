# Quickstart & Validation Guide: uv Package Management

**Feature**: `005-uv-package-management`  
**Date**: 2026-07-29

이 가이드는 `uv` 기반으로 리팩토링된 프로젝트 가상환경을 처음 구축하고 검증하는 실행 절차를 제공합니다.

## Prerequisites

- Python 3.10 이상
- `uv` CLI 도구 설치:
  ```bash
  curl -sSf https://astral.sh/uv/install.sh | sh
  ```

---

## Validation Scenarios

### Scenario 1: Clean 복구 및 동기화 검증 (`uv sync`)

1. 기존 가상환경 제거 (Clean test):
   ```bash
   rm -rf .venv
   ```
2. `uv sync` 명령어로 환경 복구:
   ```bash
   uv sync
   ```
3. **검증**: `.venv` 디렉토리가 생성되고 모든 필수 패키지가 가상환경에 동기화되었는지 확인.

---

### Scenario 2: 신규 패키지 추가 및 자동 Lock 검증 (`uv add`)

1. 메인 패키지 추가:
   ```bash
   uv add requests
   ```
2. **검증**: `pyproject.toml` 및 `uv.lock` 파일에 `requests` 패키지가 등록되었는지 확인.
3. 테스트 완료 후 패키지 원복:
   ```bash
   uv remove requests
   ```

---

### Scenario 3: `uv run`을 이용한 테스트 실행 검증

1. 전체 단위/통합 테스트 구동:
   ```bash
   uv run pytest
   ```
2. **검증**: 별도의 `source .venv/bin/activate` 없이 10개 전체 테스트 스위트가 정상 통과하는지 확인.
