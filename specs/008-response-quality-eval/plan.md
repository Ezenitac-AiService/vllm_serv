# Implementation Plan: 모델 답변 품질 비교 분석 및 자동 검증 테스트 구현 (Response Quality Evaluation & Benchmark)

**Branch**: `008-response-quality-eval` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/008-response-quality-eval/spec.md)

**Input**: Feature specification from `/specs/008-response-quality-eval/spec.md`

## Summary

본 계획은 서빙 대상 LLM(Qwen 3.5 2B/4B/9B 및 Gemma 4 E2B/E4B/12B)의 답변 품질을 다축 기준(지시 이행, 요약, 문맥 파악, JSON 스키마 정합성)으로 정량화하고, `ATEAM_ExtractionItem.py`(주식 댓글 화자/대상 복원) 및 `BTEAM_ExtractionItem.py`(음식점 리뷰 대상/카테고리/정제문 파이프라인)의 실무 벤치마크 워크로드를 평가 기준에 포함시켜, **[속도(TPOT) + VRAM + 품질 점수 + 실무 워크로드 수행력] 3차원 종합 가성비 지표 및 비교 보고서(`analysis_report_quality.md`)**를 자동 생성하는 테스트 및 벤치마크 엔진 구현을 목표로 합니다.

---

## Technical Context

- **Language/Version**: Python 3.10+ (uv 환경)
- **Primary Dependencies**: Pydantic v2, `pytest`, `kiwipiepy`, `rank_bm25`, `httpx`, `asyncio`, `llama.cpp` (GGUF runner)
- **Storage**: JSON/Markdown 파일 기반 레포트 저장 (`specs/008-response-quality-eval/analysis_report_quality.md`)
- **Testing**: `pytest` (`uv run pytest`)
- **Target Platform**: Linux x86_64, NVIDIA GTX 1080 Ti (11GB VRAM)
- **Project Type**: CLI / Evaluation Engine & Benchmark Automation Script
- **Performance Goals**:
  - Mock 평가 모드 테스트 실행 시간 < 1.0초 (CI/CD 즉시 검증)
  - 품질 점수 가중 알고리즘: 정량 규칙 지표 60% (JSON 스키마 30% + 슬롯 정확도 30%) + 정성 지표 40% (문맥/정제문 완결성)
- **Constraints**:
  - 11GB VRAM 한계 내 4K/8K 대용량 컨텍스트 수용성 평가 및 OOM 안전 롤백 보장
  - 기존 17개 레그레션 pytest 수트 100% 성공 유지

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (Principle I: 언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (Principle II: TDD 및 품질 보증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (Principle III: 종료 조건 명확화 원칙)
- [x] 기존 아티팩트 및 명세의 파괴적 편집을 금지하고 온전히 보존 및 확장하는가? (Principle IV: 비파괴적 문서 수정 원칙)

---

## Project Structure & Touch-Points

### Documentation (this feature)

```text
specs/008-response-quality-eval/
├── spec.md                     # Feature specification
├── plan.md                     # This implementation plan
├── research.md                 # Phase 0 output (가중 알고리즘 & 참고 워크로드 설계)
├── data-model.md               # Phase 1 output (Pydantic 엔티티 및 스키마)
├── quickstart.md               # Phase 1 output (검증 및 실행 가이드)
├── contracts/
│   └── quality-eval-schema.json # Phase 1 output (JSON 파싱 정합성 계약 규격)
└── checklists/
    └── requirements.md         # Specification quality checklist
```

### Source Code & Test Layout

```text
src/
├── eval/
│   ├── __init__.py
│   └── quality_evaluator.py    # [NEW] 다축 답변 품질 검증 및 가중 점수 산출 엔진
├── core/
│   ├── process_manager.py      # [REFERENCE] 로컬 서빙 프로세스 및 VRAM 한계 관리
│   └── llama_manager.py        # [REFERENCE] 모델 동적 스위칭 관리
scripts/
└── benchmark_quality.py        # [NEW] Qwen 3.5 & Gemma 4 3D 품질-속도-VRAM 교차 벤치마크 및 보고서 생성 스크립트

tests/
├── unit/
│   └── test_quality_evaluator.py  # [NEW] 품질 평가 가중 알고리즘 및 Pydantic 스키마 단위 테스트
└── integration/
    └── test_quality_benchmark.py  # [NEW] 품질 벤치마크 실행 및 마크다운 보고서 생성 통합 테스트
```

**Structure Decision**: 기존 `src/core/` 하위 모듈 및 레거시 워크로드 파일(`ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`)의 원본을 온전히 보존하면서, 신규 품질 평가 모듈(`src/eval/quality_evaluator.py`) 및 벤치마크 스크립트(`scripts/benchmark_quality.py`)를 추가하는 단일 프로젝트 샌드박스 구조를 채택함.

---

## Execution Phases & Milestones

### Phase 0: Research & Architecture Decisions (Completed)
- `research.md` 작성 완료:
  - 정량 60% (JSON 스키마 30% + 슬롯 정확도 30%) + 정성 40% (문맥/정제문) 가중 채점 알고리즘 도출
  - `ATEAM_ExtractionItem.py` 및 `BTEAM_ExtractionItem.py` 5단계 하이브리드 추출 파이프라인의 참고 벤치마크 워크로드화 결정
  - `Quality-per-Speed Index` 및 `Quality-per-VRAM Index` 3D 가성비 지수 공식 설계

### Phase 1: Data Model & Contracts (Completed)
- `data-model.md`, `quickstart.md`, `contracts/quality-eval-schema.json` 작성 완료:
  - `QualityBenchmarkPrompt`, `QualityEvaluationMetric`, `ComprehensiveQualityReportMetric` Pydantic 엔티티 설계

### Phase 2: Implementation & Task Generation (Next Step: `/speckit-tasks`)
- `src/eval/quality_evaluator.py` 구현 (가중 채점 및 ATEAM/BTEAM 슬롯 추출 검증)
- `tests/unit/test_quality_evaluator.py` 단위 테스트 작성
- `scripts/benchmark_quality.py` 자동화 벤치마크 스크립트 구현
- `tests/integration/test_quality_benchmark.py` 통합 테스트 작성
- 마크다운 보고서(`specs/008-response-quality-eval/analysis_report_quality.md`) 생성 검증
- 전체 17개 기존 테스트 + 신규 품질 테스트 100% 통과 검증
