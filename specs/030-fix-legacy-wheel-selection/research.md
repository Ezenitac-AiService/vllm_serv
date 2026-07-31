# Research: 구형 i7-930 타겟 사전 빌드 휠 탐색 및 오프라인 설치 메커니즘 (030-fix-legacy-wheel-selection)

## Decision 1: `llama_cpp_python` 사전 빌드 휠 명시적 매칭 및 버전 순서 정렬

- **Decision**: `scripts/setup.sh`의 Fast-Track 탐색 대상을 `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl 2>/dev/null | tail -n 1` 패턴으로 명시 지정함.
- **Rationale**: 기존 `ls wheels/legacy_i7_930/*.whl | head -n 1` 구문은 알파벳 정렬로 인해 `annotated_doc-0.0.5-py3-none-any.whl` 등 의존성 휠이 먼저 선택되어 `llama_cpp_python` C++ 휠이 복원되지 않는 치명적 오탐을 유발함. `ls -v` (version sort) 및 타겟 파일명 프리픽스 지정으로 최신 `llama_cpp_python` 휠을 정확히 선택함.
- **Alternatives Considered**:
  - `wheels/legacy_i7_930/*.whl` 전체 목록을 배열로 순회: 코드 복잡도가 높아지고 에러 처리가 번거로움.
  - `llama-cpp-python` 이외의 의존성 휠을 별도 subfolder로 분리: 시드 팩 아카이브 구조 변경 오버헤드 발생.

## Decision 2: 오프라인 패키지 주입 옵션 (`--no-index --find-links`)

- **Decision**: Fast-Track 휠 설치 실행 시 `uv pip install "$LEGACY_WHEEL" --force-reinstall --no-index --find-links wheels/legacy_i7_930` 옵션 적용.
- **Rationale**: 외부 PyPI 네트워크 연결 없이 로컬 디렉터리(`wheels/legacy_i7_930`)에 보관된 의존성 휠 패키지만을 참조하여 오프라인 고속 주입을 완성함.
- **Alternatives Considered**:
  - `--no-deps` 옵션 적용: `llama_cpp_python` 휠 설치 후 실행 시 `jinja2`나 `diskcache` 등 의존 모듈 미설치 오류 발생 위험 존재.

## Decision 3: GPU 오프로드 검증 실패 시 자동 소스 컴파일 Fallback

- **Decision**: Fast-Track 휠 설치 직후 `llama_supports_gpu_offload()` 검증 단계에서 실패(False 또는 AssertionError) 발생 시, `setup.sh`를 즉시 중단(`exit 1`)하지 않고 경고 로그 출력 후 `INSTALLED_VIA_FAST_TRACK=0`으로 전환하여 `CMAKE_ARGS` 소스 컴파일 파이프라인으로 안전 Fallback을 수행함.
- **Rationale**: 사전 빌드 휠 아티팩트가 유실/손상되었거나 아키텍처 불일치(Illegal Instruction 등)가 발생하더라도 머신 구축 파이프라인 전체가 실패하지 않고 자동 보정될 수 있도록 회복탄력성(Resilience)을 보장함.
- **Alternatives Considered**:
  - 검증 실패 시 즉시 setup.sh 중단: 레거시 머신 환경에서 수동 문제 해결 오버헤드 증가.
