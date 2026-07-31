# Feature Specification: 모델 답변 품질 비교 분석 및 자동 검증 테스트 구현 (Response Quality Evaluation & Benchmark)

**Feature Branch**: `008-response-quality-eval`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "단순히, 처음 토큰을 생성하는데까지 걸린 시간과, 토큰 생성 속도, 메모리 사용량만을 비교 분석하는게 아니라, 답변의 품질도 비교 분석 검증하는 테스트 구현"

## Clarifications

### Session 2026-07-29

- Q: 리뷰 문맥 파악, 대상/화자 추출 및 감성분석 재구성 품질 검증 방식 → A: Pydantic/JSON 스키마 기반 구조화 출력 검증 + 대상/화자 슬롯 추출 정확도(Slot Precision) 및 재구성 품질(1~5점) 종합 채점
- Q: ATEAM_ExtractionItem.py 및 BTEAM_ExtractionItem.py의 역할과 활용 방식 → A: 해당 파일들을 직접 수정/연결하는 것이 아니라, 두 파이프라인에서 정의한 실무 도메인 태스크(주식 댓글 및 음식점 리뷰의 화자/대상 복원, 5대 카테고리 추출, 정제문 생성)와 프로토콜을 **참고 평가 워크로드(Reference Benchmark Workload)**로 채택하여, 본 서비스에서 서빙되는 로컬 LLM(Qwen 3.5 / Gemma 4)의 품질 검증 테스트 데이터셋 및 벤치마크 기준으로 활용함.
- Q: 정량 지표 vs 정성 지표 종합 품질 점수 가중치 산출 방식 → A: 정량 규칙 지표 60% (JSON 스키마 정합성 30% + 슬롯 정확도 30%) + 정성 지표 40% (문맥 자연스러움 및 정제문 완결성) 결합 가중 산출 알고리즘 적용 (`Quality Score = 0.6 * Quantitative + 0.4 * Qualitative`)
- Q: 고품질 정답지(Golden Reference Dataset) 생성 및 검증 파이프라인 → A: 1단계) Antigravity(Gemini 3.6 Flash)를 Teacher 모델로 활용하여 정답 초안(Golden Ground-Truth Draft) 자동 생성 ➔ 2단계) 인간 전문가의 교정·검증(Human-in-the-Loop Review)을 거쳐 최종 고품질 Golden Ground-Truth 정답 세트(`src/eval/golden_dataset.json`) 확정 ➔ 3단계) 본 서비스 서빙 대상 로컬 LLM(Qwen 3.5 / Gemma 4) 품질 평가의 절대적 기준으로 적용

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 다축 기준 기반 모델 답변 품질 자동 평가 엔진 (Priority: P1) 🎯 MVP

시스템 엔지니어 및 테스터는 지시 이행 능력, 요약 정확도, 한국어/영어 자연스러움, 구조화 출력(JSON/Markdown) 준수 여부, 그리고 `ATEAM_ExtractionItem.py` 및 `BTEAM_ExtractionItem.py`에 정의된 실무 도메인 벤치마크 워크로드(주식 댓글 및 음식점 리뷰의 대상/화자 추출, 5대 카테고리 분류 및 감성분석용 정제문 `refined_sentence` 생성)를 참고 평가 기준으로 구동하여 각 로컬 서빙 LLM 응답의 품질 점수를 정량화할 수 있어야 합니다.

**Why this priority**: 실제 서빙 대상 모델(Qwen 3.5 / Gemma 4)이 주식 도메인(`ATEAM`) 및 음식점 도메인(`BTEAM`)의 다문맥 파악 및 복합 정제 태스크를 성공적으로 수행할 수 있는지 객관적 품질 수치로 분석 및 검증하기 위함입니다.

**Independent Test**: 품질 평가 벤치마크 스크립트를 통해 `ATEAM` 및 `BTEAM` 기준 프롬프트 데이터셋을 주입했을 때, 각 서빙 모델의 1~5점 품질 점수 및 규칙 기반 메트릭(포맷 준수, 키워드 포함율, 리뷰 대상/화자 슬롯 추출 정확도 등)이 정상 산출되는지 독립 테스트 가능합니다.

**Acceptance Scenarios**:

1. **Given** 복합 지시 프롬프트(요약, 포맷 지정, 한/영 번역) 세트가 주어졌을 때, **When** 모델이 생성한 응답을 품질 평가 엔진으로 검증하면, **Then** 포맷 준수율, 키워드 일치율, 지시 이행 점수가 계산되어 반환됩니다.
2. **Given** JSON 또는 Markdown 구조화 응답 요구 프롬프트 요청 시, **When** 모델 응답에 파싱 에러나 지시 미준수가 발생하면, **Then** 해당 평가 항목에서 감점 처리되고 상세 사유가 기록됩니다.
3. **Given** `ATEAM` (주식 댓글) 및 `BTEAM` (음식점 리뷰) 다중 문장 텍스트가 주어졌을 때, **When** 로컬 서빙 모델(Qwen 3.5 / Gemma 4)이 리뷰의 문맥을 파악하여 대상(Target), 화자(Speaker), 감성(Sentiment)을 추출하고 감성분석용 정제문(`refined_sentence`)으로 재구성하면, **Then** Pydantic/JSON 스키마 파싱 정합성 및 슬롯 추출 정확도(Slot Precision)가 정량 검증됩니다.

---

### User Story 2 - Qwen 3.5 vs Gemma 4 종합 속도-메모리-품질 교차 비교 보고서 생성 (Priority: P2)

대시보드 관리자 및 설계자는 기존 속도 지표(TTFT, TPOT) 및 VRAM 사용량과 신규 산출된 답변 품질 점수를 결합한 종합 모델 비교 보고서를 확인하고, 용도별 최적의 모델(가성비, 최고 품질, 최저 지연)을 선택할 수 있어야 합니다.

**Why this priority**: 속도, 메모리, 품질 3가지 축을 종합 비교하여 실무 환경에 적합한 최적 모델 프리셋을 도출하기 위함입니다.

**Independent Test**: 종합 벤치마크 평가 스크립트를 구동하여 속도-품질 가성비 지표가 포함된 마크다운 보고서 파일이 자동 생성되는지 테스트 가능합니다.

**Acceptance Scenarios**:

1. **Given** Qwen3.5 3종(2B, 4B, 9B) 및 Gemma 4 3종(E2B, E4B, 12B) 측정 데이터가 준비된 상태에서, **When** 종합 품질 벤치마크를 구동하면, **Then** 모델별 속도, VRAM, 품질 점수, 종합 가성비 지표가 정렬된 보고서 파일이 생성됩니다.

---

### User Story 3 - 환각(Hallucination) 및 지시 탈선 예외 감지 검증 (Priority: P3)

사용자는 모델이 거짓 정보를 생성하거나 맥락에서 벗어난 오답(Hallucination)을 작성할 때 이를 자동 탐지하고 평가 리포트에 경고 항목으로 표시받아야 합니다.

**Why this priority**: 실제 서비스 적용 시 오답이나 잘못된 정보 제공으로 인한 위험을 사전에 모니터링하고 차단하기 위함입니다.

**Independent Test**: 모순되거나 사실 확인이 필요한 프롬프트를 주입하여 환각 탐지 알고리즘이 감점 및 경고 이벤트를 올바르게 생성하는지 확인 가능합니다.

**Acceptance Scenarios**:

1. **Given** 사실 확인 프롬프트 주입 시, **When** 모델이 존재하지 않는 사실을 확신하여 답변하면, **Then** 환각 위험 지표가 높게 측정되고 보고서에 경고 항목으로 표시됩니다.

---

### Edge Cases

- **초단문 및 빈 응답 처리**: 모델이 토큰 생성 중 중단되거나 공백만을 반환하는 경우 품질 점수를 0점으로 처리하고 에러 플래그 설정.
- **포맷 깨짐 (Invalid JSON/Markdown)**: JSON 요구 프롬프트에서 JSONDecodeError 발생 시 포맷 점수 0점 감점 처리.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `ATEAM_ExtractionItem.py` (주식 댓글 추출) 및 `BTEAM_ExtractionItem.py` (음식점 리뷰 추출) 파일의 평가 도메인 프롬프트 및 파이프라인 규칙을 **참고 벤치마크 워크로드**로 도입하여, 서비스 대상 모델(Qwen 3.5 / Gemma 4)의 문맥 파악, 화자/대상 추출 정확도, 정제문 완성도를 정량 측정하는 품질 평가 엔진 구현.
- **DoD-002**: Qwen 3.5 3종 및 Gemma 4 3종 모델에 대한 [속도 + VRAM + 답변 품질 점수 + ATEAM/BTEAM 벤치마크 수행력] 3차원 종합 교차 비교 분석 보고서(`specs/008-response-quality-eval/analysis_report_quality.md`) 자동 생성 및 검증 완료.
- **DoD-003**: 기존 17개 레그레션 테스트 및 신규 품질 평가 테스트 수트 100% 통과 보장.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 Antigravity(Gemini 3.6 Flash)를 Teacher 모델로 활용해 정답 초안을 작성하고, 인간 전문가의 검증·교정(Human-in-the-Loop Verification)을 거쳐 확정된 고품질 정답지 파일(`src/eval/golden_dataset.json`)을 관리하며, 이를 로컬 서빙 모델(Qwen 3.5 / Gemma 4) 품질 채점의 기준으로 적용할 수 있어야 합니다.
- **FR-002**: 품질 평가 엔진은 응답 결과에 대해 정량 지표 60%(JSON 스키마 정합성 30% + 슬롯 추출 정확도 30%)와 정성 지표 40%(문맥 자연스러움 및 정제문 완결성)를 가중 결합하여 최종 1~5점 스케일의 품질 점수(`Quality Score = 0.6 * Quantitative + 0.4 * Qualitative`)를 자동 산출해야 합니다.
- **FR-003**: 품질 평가 엔진은 지시사항 미준수, 포맷 파싱 실패, 환각 발생에 대해 감점 항목과 상세 사유를 명시해야 합니다.
- **FR-004**: 벤치마크 스크립트는 모델별 초통 시간(TTFT), 토큰 생성 속도(TPOT), VRAM peak 사용량과 답변 품질 점수를 1:1 매핑하여 종합 가성비 지표(`Quality Score / TPOT` 및 `Quality Score / VRAM`)를 산출해야 합니다.
- **FR-005**: 벤치마크 완료 후 결과 데이터를 요약·비교하는 마크다운 분석 보고서(`specs/008-response-quality-eval/analysis_report_quality.md`)를 자동으로 생성 및 갱신해야 합니다.
- **FR-006**: 품질 검증 과정은 Mock 또는 실측 모드 모두를 지원하여 CI/CD 테스트 환경에서도 빠르게 동작할 수 있어야 합니다.
- **FR-007**: 품질 평가 엔진은 자연어 다중 문장 리뷰에 대해 대상(Target), 화자(Speaker), 감성(Sentiment), 재구성 문장(Restructured Text)을 포함하는 Pydantic/JSON 스키마 구조 검증 및 슬롯 추출 정확도(Slot Precision)를 자동 평가해야 합니다.
- **FR-008**: 품질 평가 벤치마크는 `ATEAM_ExtractionItem.py` 및 `BTEAM_ExtractionItem.py` 파일에 명시된 5단계 추출 규칙 및 검증 프로토콜을 평가 데이터셋 기준으로 반영하여, 본 서비스에서 서빙되는 로컬 LLM 라인업(Qwen 3.5 / Gemma 4)의 실무 태스크 수행력 및 정제 문장 생성 품질을 교차 분석·검증해야 합니다.

### Key Entities

- **QualityMetric**: 프롬프트 ID, 모델 ID, 포맷 준수 점수, 키워드 일치 점수, 지시 이행 점수, 종합 품질 점수(1~5점)를 담은 엔티티
- **ComprehensiveReport**: 모델별 속도(TTFT, TPOT), 메모리(VRAM), 품질 점수, 가성비 지수를 포함하는 종합 분석 레포트 엔티티

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Qwen3.5 3종 및 Gemma 4 3종 모델에 대한 답변 품질 점수가 정량적 수치(1~5점)로 측정 완료되어야 합니다.
- **SC-002**: 속도-메모리-품질 3차원 종합 지표를 바탕으로 최적의 가성비 및 최고 품질 모델 프리셋 추천안이 도출되어야 합니다.
- **SC-003**: 품질 검증 테스트 코드 추가 후에도 pytest 테스트 수트 통과율 100%를 유지해야 합니다.

## Assumptions

- 규칙 기반 품질 검사(Format Validator & Keyword Matching)와 정밀 평가 체계를 병행하여 일관된 채점 결과를 제공함을 가상합니다.
- 평가 데이터셋에는 표준 한국어/영어 서술형 및 구조화(JSON) 프롬프트가 균형 있게 포함된다고 가정합니다.
