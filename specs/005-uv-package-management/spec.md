# Feature Specification: uv 기반 가상환경 및 패키지 관리 리팩토링 (uv Package Management)

**Feature Branch**: `005-uv-package-management`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "uv를 이용한 venv 가상환경에 uv add를 이용해 라이브러리를 설치하고 추후 uv sync를 통해 복구 하는 구조로 리펙토링"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - uv 기반 신규 패키지 추가 및 의존성 고정 (Priority: P1)

개발자는 신규 라이브러리가 필요할 때 `uv add` 명령어를 사용하여 가상환경에 즉시 패키지를 설치하고, 프로젝트 표준 의존성 파일에 고정(Lock)하여 저장할 수 있어야 합니다.

**Why this priority**: 패키지 추가 시 의존성 파일이 자동으로 업데이트되어 팀원 간 환경 일관성을 유지하는 핵심 가치를 제공합니다.

**Independent Test**: `uv add <package>` 실행 후 가상환경 내 패키지 설치 여부 및 프로젝트 설정 파일(`pyproject.toml`, `uv.lock`)에 해당 패키지와 버전 정보가 올바르게 추가되었는지 독립적으로 테스트할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** uv 프로젝트 환경이 구성되어 있을 때, **When** 개발자가 `uv add pytest` 명령을 실행하면, **Then** 시스템은 가상환경에 `pytest`를 설치하고 `pyproject.toml` 및 `uv.lock`에 해당 의존성을 추가한다.
2. **Given** 특정 버전 또는 개발용 패키지가 필요할 때, **When** 개발자가 `uv add --dev <package>` 또는 버전 명시 설치를 수행하면, **Then** 해당 구분에 맞게 의존성이 분류되어 등록된다.

---

### User Story 2 - uv sync를 통한 일관된 가상환경 복구 (Priority: P1)

새로운 개발자가 저장소를 클론하거나 CI/CD 파이프라인이 실행될 때, `uv sync` 한 번으로 동결된 의존성 잠금 파일(`uv.lock`) 기준의 가상환경을 100% 동일하게 빠르게 복구해야 합니다.

**Why this priority**: 프로젝트의 환경 재현성을 확보하여 "내 컴퓨터에서는 되는데..." 문제를 근본적으로 해결합니다.

**Independent Test**: 새로운 clean 환경에서 `uv sync` 실행 시 단일 명령어로 프로젝트에 명시된 모든 패키지와 정확한 버전이 가상환경에 복구되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** `pyproject.toml`과 `uv.lock` 파일이 존재하는 상태에서 가상환경이 비어있거나 생성이 필요한 경우, **When** 사용자가 `uv sync` 명령을 실행하면, **Then** 시스템은 `.venv` 가상환경을 생성하고 잠금 파일에 명시된 정확한 버전의 패키지들을 모두 설치한다.
2. **Given** 기존 가상환경에 불필요하거나 잠금 파일에 없는 패키지가 섞여 있을 때, **When** `uv sync`를 실행하면, **Then** 잠금 파일과 일치하도록 가상환경을 깨끗하게 동기화한다.

---

### User Story 3 - 프로젝트 빌드/테스트 스크립트 uv 호환 리팩토링 (Priority: P2)

기존 프로젝트의 실행, 테스트, 검증 스크립트 및 문서(Quickstart 등)가 기존 `pip` / `venv` 방식에서 `uv` 기반 커맨드로 일관되게 업데이트되어야 합니다.

**Why this priority**: 개발자가 혼선 없이 uv 체계 내에서 테스트 및 서버를 구동할 수 있도록 개발 경험(DX)을 정립합니다.

**Independent Test**: 프로젝트 테스트 명령어(`pytest` 등) 및 서버 구동 명령어가 `uv run` 또는 uv 가상환경 활성화 상태에서 정상적으로 구동되는지 테스트합니다.

**Acceptance Scenarios**:

1. **Given** uv 동기화가 완료된 가상환경에서, **When** 사용자가 `uv run pytest` 명령을 실행하면, **Then** 프로젝트 전체 테스트 스위트가 가상환경 내에서 실패 없이 구동된다.
2. **Given** 개발자가 프로젝트 시작 가이드를 볼 때, **When** 환경 구축 안내 구문을 확인하면, **Then** `uv sync` 기반의 단일 복구 단계가 제공된다.

---

### Edge Cases

- 시스템에 `uv` 도구가 설치되어 있지 않은 경우 사용자에게 설치 안내 메시지를 어떻게 노출할 것인가?
- 기존 `requirements.txt` 파일이 존재하는 경우 `pyproject.toml`로 기존 의존성을 손실 없이 이관하는 방법은 무엇인가?
- Python 인터프리터 버전 미스매치 발생 시 `uv`가 프로젝트 지정 Python 버전을 자동 다운로드/연동하여 정상 처리하는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 프로젝트 루트에 `pyproject.toml` 및 `uv.lock` 파일이 정상적으로 정의되고 관리되어야 한다.
- **DoD-002**: Clean 환경에서 `uv sync` 명령 단 1회 실행으로 모든 패키지 의존성이 가상환경(`.venv`)에 복구되고, `uv run pytest`로 전체 단위/통합 테스트가 통과해야 한다.
- **DoD-003**: 프로젝트 구축 및 개발 안내 문서(README/Quickstart)가 `uv` 기반 명령 체계로 모두 교체되어야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 프로젝트는 Python 패키지 및 의존성 관리를 위해 standard `pyproject.toml` 및 `uv.lock` 기반 표준 구조를 채택해야 한다.
- **FR-002**: 신규 패키지 설치 시 반드시 `uv add <package>` (개발 의존성은 `uv add --dev <package>`) 명령을 사용하여 의존성을 기록해야 한다.
- **FR-003**: 가상환경 재현 및 복구는 `uv sync` 명령어를 통해 `uv.lock`에 명시된 버전과 100% 동일하도록 격리 복구되어야 한다.
- **FR-004**: 시스템 실행 및 테스트 수행은 `uv run` 환경 구동 또는 uv 가상환경 경로(`.venv`)를 사용하도록 스크립트 및 구동 환경을 통합해야 한다.
- **FR-005**: 기존 프로젝트의 패키지 목록(`src` 및 `tests`에서 사용 중인 fastapi, httpx, pytest, sse-starlette 등)은 누락 없이 `pyproject.toml` 메인/개발 의존성에 포함되어야 한다.

### Key Entities

- **ProjectConfiguration (`pyproject.toml`)**: 프로젝트 이름, 버전, 메인 의존성(dependencies), 개발 의존성(dev-dependencies) 정보
- **Lockfile (`uv.lock`)**: 패키지별 exact 버전, 해시 및 전의적 의존성(transitive dependencies) 정보를 담은 고정 파일

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 신규 환경 구축 및 의존성 복구 시간이 `uv sync` 도입으로 기존 대비 3배 이상 단축된다.
- **SC-002**: `uv sync` 실행 후 패키지 버전 미스매치로 인한 실행 오류 발생율 0%를 달성한다.
- **SC-003**: 신규 개발자가 프로젝트 환경을 세팅하는 명령어가 단 1개(`uv sync`)로 단순화된다.

## Assumptions

- 프로젝트 개발 및 실행 환경에 `uv` CLI 도구가 설치되어 있거나 표준 안내(`curl -sSf https://astral.sh/uv/install.sh | sh`)를 통해 쉽게 설치 가능하다고 가정한다.
- 가상환경 디렉토리의 기본 경로는 `.venv`로 설정한다.
- 기존 소스 코드(`src/`, `tests/`)는 외부 패키지 임포트 변경 없이 동일하게 동작한다고 가정한다.
