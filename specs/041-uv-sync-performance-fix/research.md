# Phase 0 Research: setup.sh uv sync 속도 최적화 및 로컬 격리 고속화 (041-uv-sync-performance-fix)

## Research Decisions

### 1. `uv sync --frozen` vs `uv sync` 동작 매커니즘
- **Decision**: `uv.lock` 파일과 `.venv` 가상환경이 존재하는 상황에서는 `uv sync --frozen`을 우선 실행하고, 실패 시 일반 `uv sync`로 자동 Fallback합니다.
- **Rationale**: `uv sync --frozen`은 `uv.lock` 파일을 기준으로 PyPI 원격 패키지 인덱스 재조회 및 의존성 재해석(Resolution) 과정을 100% 바이패스합니다. 이를 통해 지연 시간을 수십 초에서 1초 미만으로 단축시킵니다.
- **Alternatives Considered**: 
  - `uv sync --offline`: 로컬 캐시만 사용하지만 lockfile이 개정되었을 때 동기화가 실패할 수 있음.
  - `.venv` 디렉토리 체크 후 `uv sync` 완전 스킵: 패키지가 훼손된 경우 복구가 불가능함. `uv sync --frozen`이 안전하면서도 최고속 검증 방식임.

### 2. 최초 설치 환경(Lockfile/Virtualenv 부재 시) 수용
- **Decision**: `[ -f "uv.lock" ] && [ -d ".venv" ]` 조건 판단 및 `uv sync --frozen` 시도 후 오류 발생 시 일반 `uv sync` 구문으로 자동 Fallback.
- **Rationale**: 최초 서버 배포나 클린 설치 환경에서도 스크립트 수정 없이 유연하게 가상환경을 자동 생성/수립할 수 있음.

---

## Technical Context Summary

- **Language/Version**: POSIX Bash, Python 3.10+
- **Tooling**: uv package manager (v0.11+)
- **Primary Goal**: `setup.sh` Step 2 실행 시간 <2초 달성
