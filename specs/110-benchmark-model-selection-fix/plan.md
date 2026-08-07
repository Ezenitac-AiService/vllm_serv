# Implementation Plan: 벤치마크 파이프라인 최적 모델 및 컨텍스트 윈도우 동적 선정 로직 정상화 (Fix Benchmark Model & Context Window Selection Logic)

**Branch**: `110-benchmark-model-selection-fix` | **Date**: 2026-08-07 | **Spec**: [`spec.md`](./spec.md)

**Input**: Feature specification from `/specs/110-benchmark-model-selection-fix/spec.md`

---

## Summary

`scripts/benchmark_context_window.py`의 `evaluate_all_catalog_models` 함수에서 벤치마크 결과 딕셔너리의 키 불일치(`benchmark_tps` vs `tpot_tok_per_sec`, `recommended_context_window` vs `recommended_context_length`)로 발생하던 디폴트 값 수렴(`tps=30.0`, `ctx=4096`) 및 첫 번째 후보 모델 기계적 선택 결함을 전면 수정한다. C-B-A 혼합 정렬 알고리즘(1단계: 파라미터 퀄리티 및 8K Fallback, 2단계: 복합 평가 점수, 3단계: max n_ctx/TPS 내림차순)을 도입하여 이진 탐색으로 실측된 dynamic context window 크기 및 최고 서빙 모델이 Stage 4 설정 파일에 100% 동적 반영되도록 개선한다.

---

## Technical Context

**Language/Version**: Python 3.12 (uv 가상환경 격리 표준)  
**Primary Dependencies**: llama-cpp-python, FastAPI, PyYAML, pytest, pydantic  
**Storage**: 로컬 파일 시스템 (`config/server_config.json`, `config/model_context_profiles.json`, `config/model_catalog.json`)  
**Testing**: pytest (`uv run pytest tests/unit/test_benchmark_context.py`)  
**Target Platform**: Linux x86_64 (NVIDIA CUDA GPU)  
**Project Type**: CLI / LLM 인퍼런스 서빙 엔진 및 벤치마킹 모듈  
**Performance Goals**: C-B-A 정렬 알고리즘 연산 시간 < 10ms, `save_benchmark_profile` 동적 반영 100% 보장  
**Constraints**: Zero Hardcoding, 실물 시스템 실측 검증, uv run 가상환경 격리, 한국어 문서화  
**Scale/Scope**: 12개 카탈로그 LLM 후보 모델  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (`tests/unit/test_benchmark_context.py` 수록 계획)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙 준수)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (DoD-001 ~ DoD-003 확립)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (기존 배경 및 승인 기록 보수 준수)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (`uv run pytest` 수록)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (전체 회귀 테스트 통과 원칙 준수)

---

## Project Structure

### Documentation (this feature)

```text
specs/110-benchmark-model-selection-fix/
├── plan.md              # 이 문서 (/speckit-plan 생성)
├── research.md          # 0단계 기술 조사서 (/speckit-plan 생성)
├── data-model.md        # 1단계 데이터 모델 정의서 (/speckit-plan 생성)
├── quickstart.md        # 1단계 검증 시나리오 가이드 (/speckit-plan 생성)
├── contracts/           # 1단계 CLI 및 인터페이스 계약서 (/speckit-plan 생성)
│   └── benchmark_contract.md
└── tasks.md             # 2단계 구체적 과제 목록 (/speckit-tasks 생성)
```

### Source Code Touchpoints

```text
scripts/
└── benchmark_context_window.py   # evaluate_all_catalog_models & C-B-A 정렬 수록

src/
├── core/
│   └── config_manager.py         # 프로필 및 서버 설정 동적 저장 모듈
└── services/

tests/
└── unit/
    └── test_benchmark_context.py # 스키마 키 매칭 및 C-B-A 정렬 단위 테스트
```

**Structure Decision**: Single project layout with root `scripts/benchmark_context_window.py` and `tests/unit/test_benchmark_context.py`.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
