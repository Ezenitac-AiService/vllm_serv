# Feature Specification: Qwen3.5 모델 3종 (2B, 4B, 9B) 서비스 추가 및 성능 검증 (Qwen3.5 Model Support & Benchmarking)

**Feature Branch**: `007-qwen35-model-support`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Qwen/Qwen3.5 2b 4b 9b 를 서비스 모델에 추가, analysis_report.md 에서 했던 것처럼 qwen3.5 모델도 서비스 성능에 대한 테스트 검증 진행"

## Clarifications

### Session 2026-07-29

- Q: Qwen3.5 모델 양자화 포맷 (Quantization Precision) → A: GPU VRAM 수용 여부를 검증하면서 Q4_K_M, Q4_0, Q8_0 3개 양자화 버전 모두를 벤치마크 검증 대상으로 포함하여 실측 비교를 수행하고, 분석 보고서를 바탕으로 최종 서비스 사용 모델 및 양자화 포맷을 선정함.
- Q: 기존 Gemma 4 모델 벤치마크 재검증 및 Qwen3.5 비교 검증 여부 → A: 리팩토링된 최신 파이프라인 구조 기반으로 기존 Gemma 4 모델 라인업(E2B, E4B, 12B)도 다시 성능 측정 대상에 포함하여, [Gemma 4 3종 + Qwen3.5 3종 (양자화 버전 포함)] 교차 비교 벤치마크 분석 보고서를 종합 작성함.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Qwen3.5 모델 라인업 사전 설정 및 동적 교체 (Priority: P1) 🎯 MVP

대시보드 관리자는 기존 Gemma 4 모델 외에도 새로 추가된 Qwen3.5 3종 모델(2B, 4B, 9B)을 대시보드 UI 및 API 사전 설정 목록에서 확인하고, 원하는 모델과 컨텍스트 크기를 선택하여 동적으로 서비스 프로세스를 로드/교체할 수 있어야 합니다.

**Why this priority**: 서비스에서 지원하는 LLM 모델 라인업을 Qwen3.5 시리즈로 확장하여 사용자가 모델별 특성 및 크기에 맞춰 선택할 수 있도록 하기 위한 핵심 기능입니다.

**Independent Test**: 대시보드 API (`/dashboard/api/capabilities` 및 `/dashboard/api/apply`)를 통해 Qwen3.5 2B, 4B, 9B 프리셋 선택 시 해당 모델 프로세스가 에러 없이 로드되고 SSE 상태 이벤트가 `READY`로 전환됨을 독립 테스트 가능합니다.

**Acceptance Scenarios**:

1. **Given** Qwen3.5 2B, 4B, 9B 프리셋이 사전 구성된 상태에서, **When** `/dashboard/api/capabilities`를 요청하면, **Then** Qwen3.5 모델 3종의 ID 및 권장 VRAM 임계값이 반환됩니다.
2. **Given** 서비스가 구동 중인 상태에서, **When** 대시보드에서 `qwen3.5-2b`, `qwen3.5-4b`, 또는 `qwen3.5-9b` 프리셋을 선택하고 적용하면, **Then** 기존 프로세스가 안전하게 종료되고 선택한 Qwen3.5 모델 서브프로세스가 새로운 파라미터로 구동됩니다.

---

### User Story 2 - Qwen3.5 성능 측정 및 분석 보고서 생성 (Priority: P1)

시스템 관리자 및 엔지니어는 Qwen3.5 3종 모델(2B, 4B, 9B)에 대하여 실제 프롬프트와 컨텍스트 크기(예: 4K, 8K)에 따른 모델 로딩 시간, 초통 응답 시간(TTFT), 토큰 생성 속도(TPOT, tokens/sec), 피크 VRAM 사용량을 자동으로 측정하고 정밀 검증 보고서를 생성받아야 합니다.

**Why this priority**: 신규 지원 모델의 서비스 적합성, 메모리 한계점(OOM 여부), 속도 경쟁력을 실측 데이터를 통해 수치적으로 검증하고 운영 기준을 확립하기 위함입니다.

**Independent Test**: Qwen3.5 자동 벤치마크 테스트 수트를 실행하여 3종 모델에 대한 측정 지표가 정리된 분석 보고서 파일이 정상 생성되는지 검증 가능합니다.

**Acceptance Scenarios**:

1. **Given** Qwen3.5 3종 모델 파일 및 벤치마크 프롬프트 세트가 준비된 상태에서, **When** 벤치마크 검증 스크립트를 구동하면, **Then** 각 모델별 모델 로딩 시간, 초통 소요시간(TTFT), 추론 속도(tokens/s), VRAM 사용량이 수집됩니다.
2. **Given** 벤치마크 측정이 완료되면, **Then** 측정된 결과를 바탕으로 각 모델의 VRAM 안정성, 4K/8K 컨텍스트 수용 가능 여부 및 권장 운용 파라미터가 정리된 분석 보고서가 생성됩니다.

---

### User Story 3 - Qwen3.5 모델 가용성 및 안전성 예외 처리 (Priority: P2)

사용자는 Qwen3.5 모델 파일이 로컬 디렉토리에 없거나 VRAM 한계를 초과하는 파라미터가 입력되었을 때 적절한 안내 및 에러 처리 메시지를 전달받아야 합니다.

**Why this priority**: 모델 다운로드 미완료 또는 메모리 부족으로 인한 서버 다운이나 무응답 상태를 방지하여 대시보드의 안정성을 유지하기 위함입니다.

**Independent Test**: 존재하지 않는 Qwen3.5 모델 경로나 과도한 컨텍스트 크기 요청 시 상태가 `ERROR`로 안전하게 전환되고 에러 메세지가 SSE로 전달되는지 테스트 가능합니다.

**Acceptance Scenarios**:

1. **Given** 지정된 Qwen3.5 모델 파일이 존재하지 않는 상태에서, **When** 해당 프리셋 적용을 요청하면, **Then** 서버 상태가 `ERROR`로 변경되고 명확한 파일 미존재 에러 메시지가 응답/SSE로 전달됩니다.

---

### Edge Cases

- **Qwen3.5 9B OOM 발상**: 11GB VRAM (예: GTX 1080 Ti) 환경에서 9B 모델 8K 컨텍스트 로딩 시 VRAM 초과가 발생하면 시스템이 멈추지 않고 Safe Error Handling 및 VRAM 롤백이 수행되어야 함.
- **아키텍처/클립 모델 차이**: Qwen3.5 모델의 비전/멀티모달 CLIP 프로젝터 및 채팅 템플릿 차이로 인한 파싱 오류가 발생하지 않도록 인수 체계 검증.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: Qwen3.5 2B, 4B, 9B 3종 모델 프리셋이 `ProcessManager` 및 `dashboard_api`에 등록되어 선택 및 구동이 완료되어야 한다.
- **DoD-002**: 기존 Gemma 4 3종(E2B, E4B, 12B) 재측정 지표와 신규 Qwen3.5 3종(2B, 4B, 9B, 양자화 포맷별) 측정 지표가 통합 비교된 교차 성능 분석 보고서가 작성되어야 한다.
- **DoD-003**: 기존 Gemma 4 모델 동적 교체 기능 및 기존 13개 단위/통합 레그레션 테스트가 100% 성공을 유지해야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 Qwen3.5 시리즈 3종 모델 식별자(`qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`)를 서비스 프리셋 목록에 추가하고 모델 파일 경로를 매핑할 수 있어야 합니다.
- **FR-002**: `ProcessManager` 및 `LlamaManager`는 Qwen3.5 3종 모델의 하드웨어 VRAM 권장 한계치(예: 2B: 6GB, 4B: 10GB, 9B: 18GB 등)를 조회할 수 있어야 합니다.
- **FR-003**: 벤치마크 테스트 엔진은 Qwen3.5 3종 모델에 대하여 단일/다중 프롬프트 입력 시 로딩 시간(초), 초통 시간(TTFT), 토큰 생성 속도(tokens/s), 피크 VRAM(MB)을 정밀 측정해야 합니다.
- **FR-004**: 벤치마크 검증 완료 후, 결과 데이터를 요약·비교하는 성능 분석 보고서(`analysis_report_qwen35.md` 또는 종합 분석 보고서)를 자동으로 생성/갱신해야 합니다.
- **FR-005**: Qwen3.5 모델 동적 스위칭 시 기존 503 Maintenance Mode 및 SSE 실시간 동기화 상태 이벤트를 동일하게 유지해야 합니다.
- **FR-006**: 벤치마크 검증 시 더미/목업 데이터를 배제하고 실제 한국어/영어 테스트 프롬프트를 사용하여 4K 이상 컨텍스트에서의 동작을 실측해야 합니다.
- **FR-007**: Qwen3.5 3종 모델에 대해 3가지 양자화 포맷(Q4_K_M, Q4_0, Q8_0) 모두를 테스트 검증 대상으로 지정하고 GPU VRAM 실측 결과에 따라 최적 포맷을 선택해야 합니다.
- **FR-008**: 벤치마크 검증 엔진은 리팩토링된 최신 서브프로세스 파이프라인 상에서 기존 Gemma 4 모델 3종(E2B, E4B, 12B)에 대한 성능 재측정을 구동하여 Qwen3.5 모델군과의 1:1 상대 성능 및 VRAM 효율성 비교 보고서를 산출해야 합니다.
- **FR-009**: ProcessManager는 Qwen3.5 모델 구동 시 아키텍처별 맞춤 채팅 템플릿(ChatML/Qwen Format) 인자를 동적으로 바인딩하여 프롬프트 포맷 왜곡을 차단해야 합니다.
- **FR-010**: 벤치마크 엔진은 11GB VRAM 한계 초과 시 9B Q8_0 등 고용량 모델의 OOM 사전 감지(Dry-run VRAM Calculation) 및 서브프로세스 안전 롤백 메커니즘을 적용해야 합니다.
- **FR-011**: 성능 검증 시 단계별 표준 한국어/영어 실무 프롬프트 데이터셋(Short: 100t, Medium: 1000t, Long: 4000t, 8000t)을 주입하여 컨텍스트 길이에 따른 부하 정밀도를 확보해야 합니다.

### Key Entities

- **QwenModelPreset**: Qwen3.5 모델 ID, GGUF 파일 경로, CLIP 프로젝터 경로, 기본 컨텍스트 크기, VRAM 한계 정보를 캡슐화한 불변 프리셋 엔티티
- **QwenPerformanceReport**: Qwen3.5 2B/4B/9B 모델별 측정 결과(로딩 시간, TTFT, TPOT, VRAM 피크, OOM 여부)를 정리한 성능 분석 레포트 엔티티

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Qwen3.5 2B, 4B, 9B 3종 모델 모두에 대한 로딩 및 텍스트 생성 벤치마크 측정이 완료되고 수치 데이터가 확보되어야 합니다.
- **SC-002**: 벤치마크 분석 보고서를 통해 VRAM 한계 내에서 4K/8K 컨텍스트를 가장 효율적으로 수용 가능한 최적의 Qwen3.5 모델 프리셋 추천안이 도출되어야 합니다.
- **SC-003**: 모델 추가 후에도 기존 테스트 수트 통과율 100% 및 API 응답 지연 시간 증가 0%를 달성해야 합니다.

## Assumptions

- Qwen3.5 GGUF 양자화 모델 파일(`qwen-3.5-2b-instruct-q4_0.gguf` 등)이 로컬 저장소 디렉토리 또는 Hugging Face를 통해 준비되어 있거나 경로가 지정 가능하다고 가정합니다.
- llama.cpp / llama_cpp_python 서버 엔진이 Qwen3.5 아키텍처 모델의 추론 및 GGUF 포맷을 지원한다고 가정합니다.
