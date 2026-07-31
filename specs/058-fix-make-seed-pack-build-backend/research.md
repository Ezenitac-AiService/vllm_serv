# Phase 0 Research: make_seed_pack.sh 빌드 백엔드(scikit-build-core) 미설치 오류 해결 (058-fix-make-seed-pack-build-backend)

## Decision 1: `make_seed_pack.sh` `uv run pip wheel` 구문에서 `--no-build-isolation` 제거

- **Decision**: `scripts/make_seed_pack.sh`의 휠 생성 명령에서 `--no-build-isolation` 옵션을 제거한다.
- **Rationale**: `--no-build-isolation` 옵션은 pip가 임시 격리 빌드 환경(isolated build environment)을 생성하지 않고 호스트 가상환경에 설치된 패키지만 사용하도록 강제한다. 그러나 `llama-cpp-python`의 pyproject.toml 백엔드인 `scikit-build-core`가 가상환경에 없으면 `BackendUnavailable: Cannot import 'scikit_build_core.build'` 크래시가 발생한다. PEP 517/518 격리 빌드를 허용하면 `uv`/`pip`가 임시 환경에 `scikit-build-core` 및 `cmake`를 자동으로 다운로드/사용하여 휠을 깨끗이 빌드한다.
- **Alternatives Considered**:
  - *Option 1: 가상환경에 `scikit-build-core` 및 `cmake`를 사전 설치하고 `--no-build-isolation` 유지* -> 패키지 매니저가 깨끗한 독립 환경이 아닐 때 버전 오염 위험 존재.
  - *Option 2 (선택된 Option C)*: `--no-build-isolation`을 제거하면서 동시에 `pyproject.toml` 및 프로젝트 빌드 의존성에 `scikit-build-core` 및 `cmake` 선언을 보강하는 이중 방어 방식 적용.

---

## Decision 2: `pyproject.toml` 및 빌드 환경 의존성 보강

- **Decision**: `pyproject.toml`의 `[build-system]` 또는 dependencies / dev dependencies 그룹에 `scikit-build-core` 및 `cmake`를 보강 등록한다.
- **Rationale**: 오프라인 빌드 또는 사전 빌드 수행 시 환경에 백엔드가 설치되어 있으면 온디맨드 빌드 및 빠른 컴파일이 모두 보장된다.
- **Alternatives Considered**: 단순 스크립트만 수정하는 방식 -> 가상환경 직접 컴파일 시 백엔드 미설치로 인한 오염 위험이 남아있음.
