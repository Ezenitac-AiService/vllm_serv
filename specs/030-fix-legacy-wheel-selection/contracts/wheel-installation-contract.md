# Contract: setup.sh Fast-Track 휠 탐색 및 오프라인 주입 CLI 인터페이스 계약 (030-fix-legacy-wheel-selection)

## 1. 휠 탐색 및 매칭 규약

- **입력 디렉터리**: `wheels/legacy_i7_930/`
- **탐색 매칭 명령어**:
  ```bash
  LEGACY_WHEEL=$(ls -v wheels/legacy_i7_930/llama_cpp_python*.whl 2>/dev/null | tail -n 1 || true)
  ```
- **매칭 조건**:
  - `LEGACY_WHEEL` 변수가 비어있지 않고 (`[ -n "$LEGACY_WHEEL" ]`), 실존하는 파일(`[ -f "$LEGACY_WHEEL" ]`)이어야 함.
  - 알파벳순 정렬로 인한 `annotated_doc` 등 타 패키지 휠의 잘못된 매칭 금지.

## 2. 오프라인 고속 주입 명령어 규약

- **실행 명령어**:
  ```bash
  uv pip install "$LEGACY_WHEEL" --force-reinstall --no-index --find-links wheels/legacy_i7_930
  ```
- **주요 인자 의미**:
  - `--force-reinstall`: 기존 기본/CPU 버전 휠을 강제 덮어쓰기
  - `--no-index`: PyPI 등 외부 네트워크 패키지 인덱스 연결 차단
  - `--find-links wheels/legacy_i7_930`: 로컬 디렉터리 내 의존성 휠 패키지 참조

## 3. GPU 오프로드 검증 및 Fallback 전환 계약

- **검증 명령**:
  ```bash
  uv run python -c "
  import llama_cpp
  fn = getattr(llama_cpp, 'llama_supports_gpu_offload', None) or getattr(llama_cpp, 'llama_supports_gpu', None)
  assert fn is not None, 'No GPU check function found'
  assert fn(), 'GPU offload not supported'
  "
  ```
- **Fallback 계약**:
  - Fast-Track 설치 시도 중 휠 파일 미존재, `uv pip install` 실패, 또는 `llama_supports_gpu_offload()` 검증 실패 발생 시:
    1. `log_warn` 경고 메시지 출력
    2. `INSTALLED_VIA_FAST_TRACK=0`으로 설정
    3. `setup.sh` 파이프라인 중단 없이 다음 단계의 `CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install ...` 소스 컴파일 파이프라인으로 전환
