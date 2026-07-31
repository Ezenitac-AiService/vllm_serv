# Implementation Plan: Fast-Track 휠 검증 서브쉘 종료 코드 캡처 구문 수정 및 C++ 소스 재컴파일 Fallback 정상 전이 보장 (056-fix-subshell-status-code-fallback)

**User Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/056-fix-subshell-status-code-fallback/spec.md)  
**Research**: [`research.md`](file:///home/dev/storage/vllm_serv/specs/056-fix-subshell-status-code-fallback/research.md)  
**Data Model & Architecture**: [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/056-fix-subshell-status-code-fallback/data-model.md)  
**API Contract**: [`contracts/fallback-pipeline-api.json`](file:///home/dev/storage/vllm_serv/specs/056-fix-subshell-status-code-fallback/contracts/fallback-pipeline-api.json)  
**Quickstart**: [`quickstart.md`](file:///home/dev/storage/vllm_serv/specs/056-fix-subshell-status-code-fallback/quickstart.md)  

---

## 1. Technical Context & Overview

이관 타겟 서버(Intel i7-930 + GTX 1070)에서 `./setup.sh` 구동 시 사전 빌드 휠 GPU 오프로드 검증 서브쉘 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1 || true)`이 `|| true`로 인해 종료 코드 0으로 오탐되어 C++ 소스 재컴파일 Fallback이 스킵되고 CPU 전용 모드로 남는 결함이 발견되었습니다.

본 구현 계획은:
1. `scripts/setup.sh` 내 서브쉘 변수 할당을 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1) || GPU_CHECK_STATUS=$?`로 수정하여 `set -e` 하에서도 실패 코드(`GPU_CHECK_STATUS != 0`)를 100% 캡처함.
2. 사전 휠 오프로드 검증 실패 시 Tier 4 C++ 재컴파일 진입 전 `uv pip uninstall llama-cpp-python`으로 실패 패키지를 자동 정리(Clean) 후 `DETECTED_CMAKE_ARGS` 기반 소스 컴파일 파이프라인으로 100% 자동 전이함.
3. `src/core/cpu_detector.py`의 `check_hardware_preflight()` 및 `start_server.sh` 구동 단계에 `llama_cpp.llama_supports_gpu_offload()` 검증을 추가하여 Fail-Fast 2중 방어선을 구축함.

---

## 2. Constitution Check & Gate Evaluation

- **Principle I (Language Policy)**: 모든 문서, 코멘트 및 소통은 한국어(Korean)로 작성됨. (Pass)
- **Principle II (Real-Integration TDD Discipline)**: 더미(Mock) 단정을 금지하고 실제 `set -e` bash 구문 및 파이썬 서브쉘 exit code 캡처 통합 테스트를 구동함. (Pass)
- **Principle III (Real-Execution & Parameterized Converge Validation)**: 수렴 검증 시 실제 스크립트를 구동함. (Pass)
- **Principle IV (Definition of Done)**: `DoD-001` ~ `DoD-004` 단정 수록. (Pass)
- **Principle V (Non-Destructive Documentation Edit)**: 비파괴적 편집 규칙 준수. (Pass)
- **Principle VI (uv Environment)**: 모든 패키지 조작 및 실행은 `uv` 사용. (Pass)
- **Principle VII (Mandatory Regression Testing)**: 전체 회귀 수트(`uv run pytest`) 100% Green 검증. (Pass)

---

## 3. Plan Phases & Touch-points

### Phase 0: Research (Completed)
- `specs/056-fix-subshell-status-code-fallback/research.md` 도출 완료.

### Phase 1: Design & Artifact Generation (Completed)
- `data-model.md`, `contracts/fallback-pipeline-api.json`, `quickstart.md` 작성 완료.

### Phase 2: Implementation Tasks Outline
- **Touch-point 1**: `scripts/setup.sh` (218행 및 267행 `GPU_CHECK_OUTPUT=$(...) || GPU_CHECK_STATUS=$?` 및 Tier 4 전 진입 `uv pip uninstall llama-cpp-python` 추가).
- **Touch-point 2**: `src/core/cpu_detector.py` (`check_hardware_preflight()` 내 `llama_cpp.llama_supports_gpu_offload()` 검증 수록).
- **Touch-point 3**: `tests/unit/test_seed_pack.py` (서브쉘 에러 코드 캡처 단위 테스트 수록).
- **Touch-point 4**: 전체 회귀 수트 실행.

---

## 4. Complexity Tracking

| Component / Subsystem | Potential Complexity | Mitigation Strategy |
|-----------------------|----------------------|---------------------|
| Bash Command Substitution | `set -e` 상에서 `VAR=$(cmd) || STATUS=$?` 실행 시 쉘 이스케이프 처리 | standard POSIX/Bash syntax 적용 및 단위 테스트 검증 |
| Package Clean Step | `uv pip uninstall` 수행 시 가상환경 락 및 툴체인 종속성 | `uv pip uninstall llama-cpp-python` 단일 패키지 지정 |
