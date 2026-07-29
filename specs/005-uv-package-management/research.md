# Research & Technical Decisions: uv 기반 가상환경 및 패키지 관리

**Feature**: `005-uv-package-management`  
**Date**: 2026-07-29

## Research Tasks & Findings

### 1. `pyproject.toml` 및 `uv.lock` 표준 사양 정의

- **Decision**: PEP 621 준수 표준 `pyproject.toml` 및 `uv` 전용 `uv.lock` 스키마 채택
- **Rationale**:
  - `uv`는 PEP 621 규격의 `[project]` 테이블 및 `[dependency-groups]` / `[build-system]` 규격을 지원함.
  - 메인 서빙용 라이브러리(`fastapi`, `httpx`, `sse-starlette`, `uvicorn`, `llama-cpp-python`)와 개발/테스트 전용 라이브러리(`pytest`, `pytest-asyncio`, `pytest-cov`)를 명확히 분리 관리.
- **Alternatives Considered**:
  - 기존 `requirements.txt` 방식 유지: 패키지 트랜지티브 의존성(Transitive Dependencies) 버전 고정이 불완전하여 환경 재현성 결여.
  - `poetry` / `pipenv` 사용: C++/Rust 확장 설치 속도가 상대적으로 느리고 `uv` 대비 동기화 성능이 떨어짐.

---

### 2. `uv add` 및 `uv sync` 명령어 워크플로우

- **Decision**:
  - 메인 패키지 추가: `uv add <package>`
  - 개발 패키지 추가: `uv add --dev <package>`
  - 환경 복구 및 격리 동기화: `uv sync`
- **Rationale**:
  - `uv add` 실행 시 `pyproject.toml`과 `uv.lock`이 즉시 갱신되어 개발자의 동기화 실수를 방지함.
  - `uv sync`는 `.venv` 가상환경이 없거나 파괴된 상태에서도 `uv.lock`에 명시된 버전과 정확히 일치하는 패키지를 수 초 내에 재설치함.
- **Alternatives Considered**:
  - `pip freeze > requirements.txt`: 플랫폼 종속적 패키지 빌드 오염 발생 위험 및 설치 속도 저하.

---

### 3. `uv run`을 통한 명령 집행 체계

- **Decision**: 테스트 실행 및 서비스 구동을 `uv run pytest` 및 `uv run python -m ...`으로 표준화
- **Rationale**:
  - `uv run`은 수동으로 `source .venv/bin/activate`를 하지 않아도 자동으로 프로젝트 `.venv` 환경을 감지하고 `PYTHONPATH` 및 venv bin 경로를 주입하여 셸 오염 없이 안정적인 테스트/서버 구동을 보장함.
- **Alternatives Considered**:
  - 쉘 수동 activation (`source .venv/bin/activate`): CI 환경이나 개별 터미널 환경에 따라 activation 미적용으로 인한 패키지 누락 예외 빈발.

---

### 4. 기존 패키지 이관 (Migration Matrix)

- **Main Dependencies**:
  - `fastapi` >= 0.100.0
  - `httpx` >= 0.24.0
  - `sse-starlette` >= 1.6.0
  - `uvicorn` >= 0.22.0
  - `pydantic` >= 2.0.0
- **Dev Dependencies**:
  - `pytest` >= 8.0.0
  - `pytest-asyncio` >= 0.23.0
  - `anyio` >= 4.0.0
