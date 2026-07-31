# Implementation Plan: uv 기반 가상환경 및 패키지 관리 리팩토링

**Branch**: `005-uv-package-management` | **Date**: 2026-07-29 | **Spec**: [spec.md](spec.md)

## Summary

본 계획서는 `vllm_serv` 프로젝트의 Python 환경 구축 및 의존성 관리를 `uv` 기반 구조로 완전 리팩토링하기 위한 아키텍처 및 실행 계획입니다. PEP 621 규격의 `pyproject.toml` 및 완전 고정 잠금 파일(`uv.lock`)을 도입하여, 개발자가 `uv add`로 신규 패키지를 안전하게 추가하고 `uv sync` 한 번으로 신규/CI 환경에서 100% 동기화된 가상환경(`.venv`)을 즉시 복구할 수 있도록 보장합니다.

## Technical Context

**Language/Version**: Python 3.10+ (uv package manager 0.1.0+)

**Primary Dependencies**: FastAPI, httpx, sse-starlette, uvicorn, pytest, pytest-asyncio

**Storage**: JSON 기반 파일 시스템 영속화 (`config/model_config.json`)

**Testing**: pytest (invoked via `uv run pytest`)

**Target Platform**: Linux Server (로컬 바인딩 전용)

**Project Type**: Web Service + Single Page Application

**Performance Goals**: `uv sync` 가상환경 복구 시간 < 3초

**Constraints**: 기존 소스 코드(`src/`, `tests/`) 내 애플리케이션 비즈니스 로직 및 모듈 임포트 구조에 변경을 주지 않고, 패키지 설치 및 실행 인프라 계층만 투명하게 리팩토링할 것.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙) -> `uv run pytest`로 기존 10개 검증 스위트 100% 통과 확인.
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙) -> spec.md에 명시 완료 (DoD-001 ~ DoD-003).

## Project Structure

### Documentation (this feature)

```text
specs/005-uv-package-management/
├── plan.md              # 이 파일
├── research.md          # uv 모범 사례 및 패키지 이관 조사
├── data-model.md        # pyproject.toml / uv.lock 사양 및 상태 정의
└── quickstart.md        # uv sync / uv add / uv run 검증 가이드
```

### Source Code (repository root)

```text
/home/dev/storage/vllm_serv/
├── pyproject.toml               # PEP 621 기반 프로젝트 메타데이터 및 의존성 정의
├── uv.lock                      # uv 고정 의존성 잠금 파일
├── .venv/                       # uv sync에 의해 생성/동기화되는 격리 가상환경
├── src/
│   ├── api/                     # FastAPI 웹 대시보드 및 추론 프록시 API
│   └── core/                    # LlamaManager 및 ConfigManager
├── tests/                       # pytest 단위 및 통합 테스트 스위트
└── specs/                       # 기능 명세서 모듈
```

**Structure Decision**: 기존 `vllm_serv` 단일 프로젝트 루트 구조를 유지하되, 패키지 및 가상환경 관리 레이어를 standard `pyproject.toml` + `uv.lock`으로 교체하는 레포지토리 전반 인프라 리팩토링 구조를 채택했습니다.
