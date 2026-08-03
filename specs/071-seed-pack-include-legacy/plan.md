# Implementation Plan: sample_05_structured_output.py의 .legacy 모듈 의존성 제거 및 시드팩 독립성 보장 명세 (071-seed-pack-include-legacy)

**Branch**: `main` (또는 `071-seed-pack-include-legacy`)
**Spec**: [`specs/071-seed-pack-include-legacy/spec.md`](spec.md)
**Created**: 2026-08-03

---

## Technical Context & Strategy

### Objective
- `samples/sample_05_structured_output.py`에서 레거시 디렉터리(`.legacy/`) 및 외부 스키마 모듈(`ATEAM_ExtractionItem`, `BTEAM_ExtractionItem`) 임포트 코드를 전면 제거.
- 표준 Pydantic `StockAnalysisResponse` 모델과 OpenAI `response_format={"type": "json_object"}` 기반의 단독(Self-contained) 예제로 스크립트를 개편하여, 향후 `.legacy` 폴더가 삭제되거나 시드 팩으로 배포된 시스템에서도 에러 없이 100% 동작하도록 보장.

### Architecture Overview
1. **Self-contained Sample Refactoring (`samples/sample_05_structured_output.py`)**
   - `sys.path.insert(..., ".legacy")` 및 `from ATEAM_ExtractionItem import ...` 참조 구문 삭제.
   - Pydantic `StockCommentItem` 및 `StockAnalysisResponse` 스키마를 이용한 단독 JSON 스키마 생성 및 `model_validate_json` 파싱 흐름으로 통합.
2. **Unit Test Alignment (`tests/unit/test_sample_scripts.py`)**
   - 단위 테스트에서 `.legacy` 모듈 없이 `sample_05_structured_output.py`가 100% 성공을 리턴하도록 수트 유지.

---

## Phase 0: Research & Analysis
- [x] **Research Completed**: [`research.md`](research.md)
  - `sample_05_structured_output.py` 독립화 구현 방안 수립 완료

---

## Phase 1: Design & Artifacts
- [x] **Data Model**: [`data-model.md`](data-model.md)
- [x] **Contracts**: [`contracts/sample_standalone_contract.json`](contracts/sample_standalone_contract.json)
- [x] **Quickstart Validation Guide**: [`quickstart.md`](quickstart.md)

---

## Phase 2: Task Planning & Execution Roadmap
1. `samples/sample_05_structured_output.py`에서 `.legacy` 디렉터리 임포트 코드 전면 제거 및 단독 Pydantic 구조화 출력 예제로 리팩토링.
2. `tests/unit/test_sample_scripts.py` 단위 테스트 실행 및 회귀 검증.
