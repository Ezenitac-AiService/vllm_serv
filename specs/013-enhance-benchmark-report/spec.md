# Feature Specification: 6-Model Comprehensive Benchmark Report, Qualitative Answer Comparison & Context Window Scaling Enhancement

**Feature Directory**: `specs/013-enhance-benchmark-report`  
**Created Date**: 2026-07-29  
**Status**: Approved (Multi-Persona Analysis Integrated)  

---

## 1. Executive Summary & User Value

현재 벤치마크 리포트(`analysis_report_quality.md`)는 6개 모델 구동 중 일부 모델이 테이블에서 누락되거나, 품질 점수(Quality Score)가 단일 숫자 수치로만 단순 표출되어 실제 모델이 어떤 문장을 생성하였고 골든 데이터셋(Ground Truth) 정답지와 어떻게 다른지 분석하기 어렵습니다. 또한 실 운영 서빙 모델 선택 시 필수 기준인 **컨텍스트 윈도우 수용 한계량(Context Window Scaling Limit)** 검증 지표가 누락되어 있습니다.

본 피처는:
1. **Gemma 4 3종(E2B, E4B, 12B) 및 Qwen 3.5 3종(2B, 4B, 9B) 총 6개 모델 전체의 실측 결과를 누락 없이 리포트 표에 표출**하고,
2. **골든 데이터셋 원문 대비 각 모델별 실제 생성 답변, ROUGE-L/슬롯 정밀도/JSON 스키마 채점 내역을 포함하는 세부 텍스트 교차 비교 섹션을 추가**하고,
3. **모델별 컨텍스트 윈도우 크기 한계량(`n_ctx`: 4K, 8K, 16K, 32K) 및 컨텍스트 증가에 따른 VRAM 점유/TTFT 지연 스케일링 측정을 포함**하고,
4. **다중 페르소나(데이터 분석가, 딥러닝 전문가, LLM 파인튜닝 전문가, 인프라 관리자, AI 아키텍트) 심층 분석 프레임워크를 리포트에 적용**하여,
실제 라이브 LLM 서버 서빙 모델 선정을 위한 완벽한 정량/정성 평가 보고서를 생성하는 것을 목표로 합니다.

---

## 2. Clarifications

### Session 2026-07-29

- Q1: 모델선정을 위한 벤치마킹 시 컨텍스트 윈도우 수용 한계량 및 VRAM/속도 변화를 보고서에 어떻게 포함할 것인가? → A: 각 모델별 지원 max context size(`n_ctx`: 4,096 / 8,192 / 16,384 / 32,768) 수용 한계량 및 컨텍스트 크기 증가 시 VRAM 점유량과 TTFT 지연 시간 확장성 측정 표를 리포트에 명시한다.
- Q2: 다중 페르소나 관점에서의 보고서 고도화 범위는 무엇인가? → A: 데이터 분석가(세부지표 분해), 딥러닝 전문가(KV 캐시/GQA/양자화 분석), 파인튜닝 전문가(골든 데이터셋 텍스트 Diff/오류 태그), 서버 관리자(11GB VRAM 한계/OOM 임계치), AI 아키텍트(3단계 서빙 추천 마이크로 아키텍처)의 5대 핵심 전문가 의견을 보고서에 차례로 녹여낸다.
- Q3: 6종 모델 전부 텍스트 전용(Pure Text LLM)으로 구동하도록 조정할 범위는 무엇인가? → A: 벤치마크 및 라이브 서빙 시 Gemma 4 멀티모달 비전 프로젝터(`clip` mmproj) 모듈 입력을 제외하고 순수 텍스트 전용 LLM 서빙으로만 프로세스를 개설하도록 설정하여 로딩 지연을 최소화하고 VRAM 점유를 경량화한다.

---

## 3. User Stories & Acceptance Scenarios

### US1: 6개 전체 모델 벤치마크 지표 완전 표출 (Priority: P1)
- **User Story**: 서비스 운영자와 연구원은 Gemma 4 3종과 Qwen 3.5 3종 총 6개 모델의 벤치마크 결과(TTFT, TPOT, VRAM, 품질 점수, 가성비 지수)를 단 하나도 누락 없이 한눈에 교차 비교하고 싶다.
- **Acceptance Criteria**:
  - [ ] 벤치마크 보고서의 비교 테이블에 `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 총 6개 모델 항목이 100% 표출되어야 함.
  - [ ] 실패하거나 헬스체크 타임아웃이 발생한 모델의 경우에도 "실패 원인 메세지"와 함께 표에 표시되어 누락이 발생하지 않아야 함.

### US2: 골든 데이터셋 vs 실제 모델 생성 답변 상세 비교 표출 (Priority: P1)
- **User Story**: 서비스 운영자는 품질 점수 숫자 외에, 골든 데이터셋 정답지 원문과 각 모델이 실제로 뱉어낸 출력 문장의 구체적 차이를 직접 눈으로 확인하고 정성 분석하고 싶다.
- **Acceptance Criteria**:
  - [ ] 보고서 내에 대표 평가 프롬프트(주식 댓글 타임라인 복원 `ATEAM-STOCK-01`, 음식점 리뷰 카테고리 추출 `BTEAM-REVIEW-01` 등)별로 **[입력 프롬프트] - [골든 데이터셋 정답] - [6개 모델별 실제 생성 답변]** 교차 비교 섹션이 포함되어야 함.
  - [ ] 각 모델별 답변 아래에 ROUGE-L Score, Exact Match 여부, JSON 파싱 통과 여부 및 오류 원인 태그(`[JSON Format Failure]`, `[Entity Hallucination]`, `[Omission]`)가 명시되어야 함.

### US3: 모델별 컨텍스트 윈도우 크기 한계량 및 스케일링 측정 (Priority: P1)
- **User Story**: LLM 서빙 모델 결정 시 긴 프롬프트(긴 문서 서머리, 대화 이력) 처리 성능과 VRAM 소모량을 예측하기 위해 각 모델별 최대 컨텍스트 윈도우 수용 한계량 및 스케일링 지표를 확인하고 싶다.
- **Acceptance Criteria**:
  - [ ] 보고서 내에 `## 4. Context Window Capacity & Scaling Limits` 섹션을 포함함.
  - [ ] 모델별 기본/최대 지원 컨텍스트 스펙(`n_ctx`: 4,096 / 8,192 / 16,384 / 32,768)과 프롬프트 길이 증가에 따른 VRAM 증가폭, TTFT 지연 시간 변화 표를 기재함.

### US4: 다중 페르소나 심층 분석 보고서 통합 (Priority: P2)
- **User Story**: AI 팀 리더와 서버 관리자는 단순 수치 목록이 아닌 5대 전문 페르소나(데이터/딥러닝/파인튜닝/인프라/아키텍트)의 심층 분석 리포트를 기반으로 즉시 서빙 모델을 결정하고 싶다.
- **Acceptance Criteria**:
  - [ ] 보고서 하단에 5개 다중 페르소나 관점의 종합 심층 검토 리포트 섹션 포함.

---

## 4. Functional Requirements (FR)

- **FR-001 (6개 모델 표출 보장)**: `scripts/benchmark_quality.py`는 벤치마크 카탈로그의 6개 모델 전체(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`)에 대해 수행 결과를 수집하고 마크다운 테이블에 6개 행 모두를 누락 없이 출력해야 한다.
- **FR-002 (골든 데이터셋 vs 모델 답변 본문 비교 섹션)**: 마크다운 리포트에 `## 3. Qualitative Sample Comparison (Golden Ground Truth vs Model Responses)` 섹션을 추가하고, 프롬프트별 정답지와 모델별 실제 텍스트 출력을 비교 표시해야 한다.
- **FR-003 (채점 세부 근거 수치 및 오류 태그 표시)**: 단순 최종 품질 점수(1~5점) 외에 ROUGE-L F1, 슬롯 복원 Exact Match, JSON 규격 준수 여부 및 감점 사유 오류 태그를 각 비교 항목에 명시해야 한다.
- **FR-004 (마크다운 접기/펼치기 UX)**: 긴 생성 답변 문장으로 인해 리포트 가독성이 떨어지지 않도록, 모델별 상세 답변 출력은 GitHub 마크다운 `<details><summary>` 접기 태그를 활용해 가독성을 최적화해야 한다.
- **FR-005 (컨텍스트 윈도우 수용 한계 및 VRAM 스케일링 측정)**: 각 모델별 지원 가능한 컨텍스트 윈도우 수용 한계량(`n_ctx`: 4,096 ~ 32,768) 및 프롬프트 길이별 Peak VRAM 점유량과 TTFT 변화 수치를 리포트 섹션 4에 명시해야 한다.
- **FR-006 (다중 페르소나 종합 평가 섹션)**: 데이터 분석가, 딥러닝 전문가, LLM 파인튜닝 전문가, 인프라 관리자, AI 아키텍트의 5대 페르소나 심층 평가 리포트를 마크다운 섹션 5에 생성해야 한다.
- **FR-007 (순수 텍스트 전용 LLM 서빙)**: 6개 모델 전체(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`) 구동 시 멀티모달 비전 프로젝터(`clip` / `--clip_model_path`) 입력을 모두 우회하고, 순수 텍스트(Pure Text) LLM 서빙 인퍼런스로 구동하여 초고속 서빙 초기화 및 VRAM 오프로드 효율성을 극대화해야 한다.

---

## 5. Success Criteria (SC)

- **SC-001 (6개 모델 표출률)**: 리포트 비교 테이블의 모델 행 수가 정확히 6개이며 누락률 0%.
- **SC-002 (실제 답변 텍스트 포함률)**: 6개 모델 각각의 실제 추론 결과 문장이 보고서 내에 100% 기재됨.
- **SC-003 (컨텍스트 윈도우 검증 포함률)**: 6개 모델 전체의 max context limits 및 VRAM/TTFT 스케일링 표 100% 포함.
- **SC-004 (다중 페르소나 분석 완비)**: 5대 페르소나별 심층 분석 보고서 항목 100% 작성 완료.

---

## 6. Assumptions & Dependencies

- **Dependencies**: `data/golden_dataset.json` (10개 정답지), `src/eval/quality_evaluator.py`, `scripts/benchmark_quality.py`.
- **Assumptions**: 벤치마크 구동 시 모델 답변 수집 데이터 구조(`ComprehensiveQualityReportMetric`)에 `raw_response`, `prompt_id`, `golden_ground_truth`, `sub_scores`, `max_context_limit`, `context_scaling_metrics` 필드를 확장 유지함.

---

## 7. Multi-Persona Deep Critical Analysis Report (다중 페르소나 심층 분석 보고서)

### 📊 1. 데이터 분석 전문가 (Data Analysis Expert)
> **"단일 스칼라 수치 점수(e.g. 3.3/5.0)는 각 지표의 역동적 상호작용을 은폐하는 심각한 착시 현상을 유발합니다."**
- **문제점 진단**: 최종 품질 점수 하나만으로 모델을 판단하면, ROUGE-L(문장 유사도)은 높지만 JSON Schema를 위반하여 서버 에러를 유발하는 모델과, 반대로 파싱은 완벽하지만 환각(Hallucination)이 있는 모델을 구분할 수 없습니다.
- **개선안**:
  1. 품질 점수를 4개 하위 지표(`ROUGE-L F1`, `Exact Match Slot Acc`, `JSON Schema Pass Rate`, `Entity Accuracy`)로 분해하여 다차원 레이다 표로 제시.
  2. 표본 편향 방지를 위해 10개 대표 프롬프트의 난이도별(단순 추출 vs 복합 타임라인 복원) 가중 평균 산출.

### 🧠 2. 딥러닝 전문가 (Deep Learning Expert)
> **"Gemma 4 아키텍처와 Qwen 3.5의 GQA/RoPE 적용 방식에 따라 컨텍스트 윈도우 증가 시 KV 캐시 VRAM 폭발 양상이 완전히 달라집니다."**
- **문제점 진단**: Gemma 4(Google/Standard Attention)는 컨텍스트가 4K에서 32K로 늘어날 때 KV 캐시가 4배 이상 급증하지만, Qwen 3.5(Alibaba/GQA)는 KV 캐시 소모량이 현저히 적습니다.
- **개선안**:
  1. `n_ctx` 수용 한계 스케일링 테스트(`4,096`, `8,192`, `16,384`, `32,768`)를 통한 KV 캐시 VRAM 소모 곡선 측정.
  2. QAT(Quantization-Aware Training `qat_q4_0`) 적용 모델과 표준 GGUF(`q4_k_m`) 간의 양자화에 따른 Perplexity/정밀도 손실 비교.

### 🎯 3. LLM 파인튜닝 & 프롬프트 엔지니어링 전문가 (LLM Fine-tuning Expert)
> **"골든 데이터셋과 실측 답변의 텍스트 레벨 Diff가 없으면 지시 이행력(Instruction Following) 실패 원인을 교정할 수 없습니다."**
- **문제점 진단**: 모델이 감점된 이유가 Chat Template 포맷 미준수 때문인지, 아니면 지시어('걔네', '이거')를 구체 명사로 바꾸지 못해서인지 눈으로 볼 수 없습니다.
- **개선안**:
  1. **[프롬프트] - [골든 데이터셋 정답] - [실제 모델 생성 문장]**을 GitHub Collapsible HTML (`<details><summary>`) 형식으로 직접 출력.
  2. 오류 유형별 태그 명시: `[JSON Format Failure]`, `[Entity Hallucination]`, `[Omission]`, `[Pronoun Unresolved]`.

### 🛠️ 4. 서버 인프라 & DevOps 관리자 (Server Infrastructure Manager)
> **"단일 GTX 1080 Ti 11GB VRAM 환경에서는 9B/12B 모델의 컨텍스트 확장 시 OOM(Out Of Memory) 붕괴 위험이 도사리고 있습니다."**
- **문제점 진단**: 9B/12B 모델을 11GB VRAM 장비에서 8K 이상 컨텍스트로 구동할 경우, KV 캐시 공간 부족으로 커널 킬(OOM)이나 TCP 소켓 타임아웃이 발생합니다.
- **개선안**:
  1. **VRAM Safety Threshold 지표** 도입: 각 모델별 OOM 발생 없이 안정 구동 가능한 최대 `n_ctx` 한계 수치 명시.
  2. 벤치마크 종료 후 평시 상주 서빙 모델(`qwen3.5-4b`) VRAM 자율 복원 가드(`try...finally`) 동작 검증.

### 🏛️ 5. AI 솔루션 아키텍트 (AI Solution Architect)
> **"운영진과 개발팀이 즉시 서빙 모델을 결정할 수 있도록 3단계 운영 배포 프레임워크를 제공해야 합니다."**
- **문제점 진단**: 단순 순위표만으로는 서비스 목적(초저지연 vs 최고 정확도 vs 가성비 서빙)에 맞는 최적 모델을 선택하기 어렵습니다.
- **개선안**:
  1. **3단계 라이브 서빙 추천 매트릭스** 제시:
     - ⚡ **최저 지연 초고속 에이전트 서빙**: `Qwen 3.5 2B` (TTFT 204ms, TPOT 64.67 tok/s, VRAM 2.45GB)
     - ⚖️ **최고 가성비 기본 서빙 (Default Resident)**: `Qwen 3.5 4B` (품질 3.3/5.0, TPOT 49.57 tok/s, VRAM 3.95GB)
     - 🎯 **최고 정밀도 배치 분석 서빙**: `Gemma 4 12B` (품질 3.3/5.0, TTFT 220ms, VRAM 8.90GB)
