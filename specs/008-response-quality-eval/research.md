# Phase 0 Research: 모델 답변 품질 비교 분석 및 자동 검증 테스트 (Response Quality Evaluation & Benchmark)

**Feature Branch**: `008-response-quality-eval`
**Date**: 2026-07-29

## Executive Summary & Research Objectives

본 연구는 서비스 대상 LLM(Qwen 3.5 2B/4B/9B 및 Gemma 4 E2B/E4B/12B)의 답변 품질을 정량화하고, 속도(TPOT, TTFT), VRAM 사용량과 결합한 **3차원 모델 효율성 검증 엔진**을 구축하기 위해 진행되었습니다. 
특히 기존 `ATEAM_ExtractionItem.py`(주식 댓글 타임라인 화자/대상 복원) 및 `BTEAM_ExtractionItem.py`(음식점 복합 리뷰 대상/카테고리/정제문 파이프라인)의 실무 워크로드를 **참고 평가 벤치마크(Reference Benchmark Workload)**로 활용하여 실무 환경에서의 정밀한 태스크 수행력을 검증합니다.

---

## 1. 정량/정성 가중 채점 알고리즘 (Quantitative vs Qualitative Scoring)

### Decision
최종 답변 품질 점수(`Quality Score`)는 **정량 규칙 지표 60% + 정성 평가 지표 40%**의 가중 결합 산출 수식으로 결정되었습니다.

$$\text{Quality Score} = 0.6 \times \text{Quantitative Score} + 0.4 \times \text{Qualitative Score}$$

- **정량 규칙 지표 (Quantitative Score, 60%)**:
  - `JSON Schema & Format Adherence (30%)`: Pydantic v2 파싱 성공 여부, 필수 필드 존재 여부, Markdown/JSON 구조 파싱 정합성
  - `Slot Extraction Precision (30%)`: `target`, `speaker`, `category` 슬롯 추출 정확도 (Kiwi 형태소 기반 키워드 및 정규식 매칭)
- **정성 평가 지표 (Qualitative Score, 40%)**:
  - `Context & Narrative Naturalness (20%)`: 문맥 보존율, 한국어/영어 문장 서술의 자연스러움
  - `Refined Sentence Completeness (20%)`: 정제문(`refined_sentence`)의 대명사/지시어 복원 및 다운스트림 감성 모델 전용 독립 문장 완결성

### Rationale
- 100% 정성 평가(LLM-as-a-Judge) 방식은 채점 시 모델의 주관성 및 비재현성 이슈가 발생할 수 있습니다.
- 100% 정량 파싱 방식은 문장의 뉘앙스 및 정제문 문맥의 자연스러움을 평가하지 못합니다.
- 6:4 가중 결합 방식을 통해 CI/CD 자동 검증의 재현성과 실무 문맥 완성도를 모두 충족할 수 있습니다.

---

## 2. 참고 벤치마크 워크로드 (Reference Benchmark Workloads: ATEAM & BTEAM)

### Decision
`ATEAM_ExtractionItem.py` 및 `BTEAM_ExtractionItem.py`에 정의된 데이터셋, 유의어 사전, 5단계 하이브리드 파이프라인(Kiwi 형태소 + BM25Okapi + NEGATIVE_PATTERNS 서브스트링 차단) 검증 규칙을 평가 스크립트(`scripts/benchmark_quality.py`)의 프롬프트 벤치마크 워크로드로 모듈화하여 탑재합니다.

- **ATEAM 워크로드**: 주식 토론방 다자간 대화 타임라인 (화자 식별, '삼전'/'하닉' 약어 및 지시어 '걔네'/'이거' 정식 종목명 복원, 5대 투자가치 분류, `refined_sentence` 생성)
- **BTEAM 워크로드**: 음식점 복합 리뷰 (5대 리뷰 카테고리 '맛'/'양'/'가격'/'청결'/'친절도', 지시어 '둘 다'/'다른 파스타' 구체 명사 복원, `refined_sentence` 생성, '마라' vs '고구마라떼' 서브스트링 차단)

### Rationale
기존 실무 훈련 코드의 프롬프트 및 비즈니스 로직 규격을 원본 변경 없이 온전히 참고 워크로드로 재활용함으로써, 로컬 서빙 모델(Qwen 3.5 / Gemma 4)이 해당 실무 5단계 추출 태스크를 얼마나 높은 정합성으로 대체할 수 있는지 정밀 평가할 수 있습니다.

---

## 3. 3차원 종합 가성비 지표 및 보고서 포맷 (3D Efficiency Indexing)

### Decision
벤치마크 결과물로 생성되는 마크다운 보고서(`analysis_report_quality.md`)에는 속도(TPOT tok/s), 메모리(Peak VRAM MB), 품질(Quality Score 1~5점) 외에 2가지 종합 가성비 지표를 산출하여 수록합니다.

1. **속도 대비 품질 지수 (Quality-per-Speed Index)**: $\frac{\text{Quality Score}}{\text{TPOT (tok/s)} \times 0.1}$
2. **메모리 대비 품질 지수 (Quality-per-VRAM Index)**: $\frac{\text{Quality Score}}{\text{Peak VRAM (GB)}}$

### Rationale
운영자 및 설계자는 단순히 품질 점수가 가장 높은 모델뿐만 아니라, 제한된 VRAM(11GB) 환경에서 메모리 및 속도 손실 대비 최고 품질을 제공하는 **Best Balanced Model**을 객관적 지수 기반으로 선택할 수 있습니다.

---

## 4. Dual-Mode (Mock vs Real Inference) 지원 체계

### Decision
평가 엔진(`QualityEvaluator`) 및 벤치마크 실행기는 **Mock 테스트 모드**와 **실제 서빙 모델 연동 모드**를 지원합니다.
- `Mock Mode`: 실제 LLM 서버 구동 없이 빠른 Pydantic 스키마 및 가중 채점 알고리즘 테스트 (CI/CD pytest 0.5초 이내 완료)
- `Real Inference Mode`: `http://127.0.0.1:8081/v1` 로컬 모델 서버와 연동하여 Qwen 3.5 및 Gemma 4 실측 평가 수행

### Rationale
TDD 원칙(Principle II)에 따라 단위 및 통합 테스트 시 100% 통과율과 빠른 반응성을 보장함과 동시에, 실환경 벤치마크 시 실제 서빙 모델의 추론 결과를 정밀 측정할 수 있습니다.
