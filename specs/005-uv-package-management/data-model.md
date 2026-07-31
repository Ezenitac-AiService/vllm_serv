# Data Model & Configuration Schemas: uv Package Management

**Feature**: `005-uv-package-management`  
**Date**: 2026-07-29

## Entities & Configuration Files

### 1. `pyproject.toml` (Project Definition Schema)

프로젝트 이름, Python 버전 요구사항, 메인 의존성 및 개발 의존성을 정의하는 표준 파일입니다.

```toml
[project]
name = "vllm-serv"
version = "0.1.0"
description = "vLLM Model Serving and Configuration Dashboard Service"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.110.0",
    "httpx>=0.27.0",
    "sse-starlette>=2.0.0",
    "uvicorn>=0.28.0",
    "pydantic>=2.6.0",
]

[dependency-groups]
dev = [
    "pytest>=8.1.0",
    "pytest-asyncio>=0.23.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

### 2. `uv.lock` (Deterministic Lockfile Entity)

`uv`에 의해 자동 생성 및 관리되는 완전 고정 의존성 잠금 파일입니다. 패키지별 Exact Version, Hashes, Transitive Dependencies를 추적합니다.

- **기능**:
  - VCS(Git)에 반드시 포함되어 팀 전체가 동일 패키지 버전을 공유함.
  - 직접 수정 금지 (`uv add`, `uv remove`, `uv lock`을 통해 자동 업데이트).

---

### 3. `.venv` (Virtual Environment Lifecycle State)

- **상태**:
  - `UNINITIALIZED`: 가상환경 미생성 상태
  - `SYNCED`: `uv.lock`과 `.venv` 내 패키지 설치 상태가 100% 동일함
  - `OUT_OF_SYNC`: `pyproject.toml` 또는 `uv.lock` 변경 후 `uv sync` 미실행 상태
