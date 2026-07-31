# Feature Specification: 성능 비교 테스트 진행 (Performance Comparison)

**Feature Branch**: `002-performance-comparison`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "제대로 찾은 허깅페이스 주소로 모델을 받고 성능 비교 테스트 진행"

## Clarifications

### Session 2026-07-10
- Q: Hugging Face 토큰 관리 방법 → A: 하드코딩을 지양하고 `/home/dev/vllm_serv/.env` 파일에 저장된 `HF_TOKEN` 환경변수를 로드하여 사용합니다.
- Q: 테스트 및 벤치마크 데이터 활용 방식 → A: 목업(Mock) 데이터, 스텁(Stub), 더미(Dummy) 데이터를 완전히 배제하고 실제 데이터를 파라미터로 주입하여 구동 및 검증하도록 리팩토링합니다.
- Q: 테스트에 주입할 실제 프롬프트의 구성 방식 → A: 다양한 길이의 단계별 한국어 프롬프트 세트(Short, Medium, 4K Long 등)를 사용하여 VRAM 사용량 증가 폭을 정밀하게 측정합니다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 모델 성능 및 VRAM 사용량 비교 (Priority: P1)

관리자는 E2B, E4B, 12B QAT 양자화 모델 3종이 정상적으로 다운로드되었는지 확인하고, 각각을 로드하여 응답 속도와 VRAM 사용량을 비교 분석할 수 있어야 합니다.

**Why this priority**: 프로젝트의 핵심 목표인 단일 사용자 환경에서의 속도와 안정성을 갖춘 최적의 모델(컨텍스트 크기 포함)을 선정하기 위한 필수 과정입니다.

**Independent Test**: 제공된 벤치마크 스크립트를 통해 세 가지 모델에 대해 순차적으로 테스트를 진행하고 결과를 리포트로 확인할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 3종의 QAT 양자화 모델이 모두 로컬에 준비된 상태에서, **When** 벤치마크 스크립트를 실행하면, **Then** 각 모델의 로딩 시간, 응답 속도(TPOT), 그리고 피크 VRAM 사용량이 출력됩니다.
2. **Given** 벤치마크 결과를 확보한 상태에서, **When** 단일 사용자 4K 컨텍스트 기준을 적용하면, **Then** GTX 1080 Ti(11GB) 한계 내에서 가장 안정적이고 빠른 모델을 선정할 수 있습니다.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: E2B, E4B, 12B 세 가지 QAT 양자화 모델에 대한 성능 측정(VRAM 사용량 및 생성 속도) 완료
- **DoD-002**: 테스트 결과를 바탕으로 단일 사용자 4K 컨텍스트 환경에 가장 적합한 최종 모델 선정 및 근거 문서화

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 저장소(`google/gemma-4-E2B-it-qat-q4_0-gguf` 등)로부터 GGUF 모델을 성공적으로 식별하고 로드할 수 있어야 합니다.
- **FR-002**: 벤치마크 도구는 모델별로 텍스트 생성 시의 속도(Tokens per second)를 정확히 측정해야 합니다.
- **FR-003**: 벤치마크 도구는 모델 로드 및 추론 중의 최대 VRAM 사용량을 측정해야 합니다.
- **FR-004**: 테스트 중 OOM(Out Of Memory)이 발생하는 모델에 대해서는 실패로 기록하고 그 한계점을 명시해야 합니다.
- **FR-005**: Hugging Face 토큰은 코드에 하드코딩하지 않고 `/home/dev/vllm_serv/.env` 파일로부터 안전하게 로드하여 다운로드 프로세스에 사용해야 합니다.
- **FR-006**: 벤치마크 테스트 및 로직 검증 시 목업(Mock)이나 더미(Dummy) 데이터를 배제하고, 실제 모델과 실제 파라미터/프롬프트를 주입하여 구동되도록 리팩토링 및 연동해야 합니다.
- **FR-007**: 성능 측정 시 다양한 길이(Short, Medium, 4K Long 등)의 한국어 프롬프트 세트를 주입하여 컨텍스트 길이에 따른 VRAM 사용량 변화를 측정해야 합니다.

### Key Entities

- **BenchmarkRunner**: 여러 모델 식별자를 입력받아 순차적으로 모델을 로드하고 테스트 프롬프트를 주입하여 성능(시간, 토큰 수) 및 시스템 자원(VRAM)을 기록하는 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 세 가지 모델 모두에 대해 최소 1회 이상의 텍스트 생성 테스트가 중단 없이(혹은 정상적인 OOM 처리와 함께) 완료되어야 합니다.
- **SC-002**: 테스트 결과를 통해 11GB VRAM 내에서 4K 컨텍스트를 안정적으로 처리하면서 응답 속도가 가장 빠른 모델이 수치적 근거(TPOT, VRAM 여유분)와 함께 1개 이상 도출되어야 합니다.

## Assumptions

- 시스템에는 python-dotenv 등 `.env` 파일을 읽어들일 수 있는 의존성이 설치되어 있거나 설치될 것입니다.
- 기존에 작성된 `benchmark.py` 스크립트를 재사용 또는 확장하여 VRAM과 TPOT 측정을 수행합니다.
- 테스트 환경은 NVIDIA GTX 1080 Ti 11GB 단일 GPU입니다.
