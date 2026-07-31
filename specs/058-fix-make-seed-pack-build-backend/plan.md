# Implementation Plan: make_seed_pack.sh 사전 휠 빌드 시 scikit-build-core 빌드 백엔드 누락 오류 해결 (058-fix-make-seed-pack-build-backend)

**Branch**: `058-fix-make-seed-pack-build-backend` | **Date**: 2026-07-31 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/058-fix-make-seed-pack-build-backend/spec.md)

**Input**: Feature specification from `/home/dev/storage/vllm_serv/specs/058-fix-make-seed-pack-build-backend/spec.md`

---

## Summary

`make_seed_pack.sh` 실행 시 레거시 사전 휠(`wheels/legacy_i7_930/*.whl`) 빌드 과정에서 `--no-build-isolation` 플래그로 인해 `pip`가 C++ 빌드 백엔드인 `scikit_build_core.build`를 임포트하지 못하고 `pip._vendor.pyproject_hooks._impl.BackendUnavailable` 크래시가 발생하는 결함을 규명하고 원천 해결합니다.

본 계획서는 `make_seed_pack.sh` 휠 빌드 구문에서 `--no-build-isolation` 옵션을 제거하여 PEP 517/518 표준 격리 환경에서 `scikit-build-core` 백엔드가 자동 조달되도록 하고, `pyproject.toml`에도 `scikit-build-core` 및 `cmake`를 명시하여 이중 방어망을 구축합니다.

---

## Technical Context

**Language/Version**: Python 3.10+, Bash shell script  
**Primary Dependencies**: `uv` (0.3+), `scikit-build-core`, `cmake`, `llama-cpp-python`  
**Storage**: Local files (`wheels/legacy_i7_930/*.whl`, `pyproject.toml`, `scripts/make_seed_pack.sh`)  
**Testing**: `pytest` (`uv run pytest tests/unit/test_seed_pack.py`), `verify_wheel_binary.py`  
**Target Platform**: Linux x86_64, Nehalem i7 930 + GTX 1070, Haswell Xeon + GTX 1080 Ti  
**Project Type**: Python CLI & Background LLM Inference Service Framework  
**Performance Goals**: `make_seed_pack.sh` 사전 휠 빌드 성공률 100%, BackendUnavailable 오류 0건  
**Constraints**: 헌법 v1.6.0 준수, Real-Integration TDD, 가상환경 격리 (`uv run`), 한국어 소통  
**Scale/Scope**: `scripts/make_seed_pack.sh`, `pyproject.toml`, `tests/unit/test_seed_pack.py`

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/058-fix-make-seed-pack-build-backend/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 Research findings
├── data-model.md        # Phase 1 Data Model & Entity definitions
├── quickstart.md        # Phase 1 Quickstart Validation Guide
├── contracts/           # Phase 1 Interface contracts
│   └── build-backend-contract.json
└── tasks.md             # Phase 2 Actionable Tasks (/speckit-tasks output)
```

### Source Code Structure (repository root)

```text
/home/dev/storage/vllm_serv/
├── pyproject.toml                             # Build dependencies configuration
├── scripts/
│   ├── make_seed_pack.sh                      # Prebuilt wheel build pipeline (--no-build-isolation removed)
│   └── verify_wheel_binary.py                 # Post-Build 3-way check script
└── tests/
    └── unit/
        └── test_seed_pack.py                  # Unit tests for build backend & wheel creation
```

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | None | All constitution principles satisfied without violations |
