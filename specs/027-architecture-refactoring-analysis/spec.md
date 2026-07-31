# Feature Specification: 2026년 7월 최신 기술 기준 서빙 파이프라인 리팩토링 및 현대화 분석 명세 (027-architecture-refactoring-analysis)

**Feature Branch**: `027-architecture-refactoring-analysis`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "2026년 7월 최신 기준으로 자료를 리서치해서 리서치한 정보를 바탕으로 프로젝트 리펙토링할 부분을 분석, 검토 해봐"

## Clarifications

### Session 2026-07-30

- Q: 2026년 7월 기준 최신 서빙 리팩토링 분석의 주요 핵심 영역 → A: 1) Speculative Decoding (추론 속도 가속), 2) Structured Output JSON Schema 보장, 3) 캔디데이트 모델 하이브리드 캐싱 및 VRAM 동적 오프로딩 구조 최적화

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 2026년 최신 LLM 서빙 동향 분석 및 리팩토링 타겟 도출 (Priority: P1) 🎯 MVP

개발자 및 시스템 엔지니어가 `vllm_serv` 서빙 파이프라인을 최신 표준으로 고도화하고자 할 때, 2026년 7월 최신 기술 스택(llama.cpp GGML 가속, Speculative Decoding, Structured Output, Pydantic v2 최적화)을 기반으로 현재 코드베이스(`src/core/`, `src/api/`)의 개선점을 분석하고 리팩토링 명세를 수립합니다.

**Why this priority**: 최신 LLM 추론 엔진 표준을 도입하여 소형 GPU(GTX 1080 Ti) 환경에서의 추론 속도(tok/s)를 극대화하고 API 기능 완성도를 완성하기 위함입니다.

**Independent Test**: `specs/027-architecture-refactoring-analysis/plan.md` 및 `research.md` 분석 결과 리포트 생성을 통해 구체적인 리팩토링 로드맵 검증 가능.

**Acceptance Scenarios**:

1. **Given** 2026년 최신 LLM 서빙 표준 기술 자료가 주어졌을 때, **When** 프로젝트 구조 분석이 진행되면, **Then** 현재 코드베이스의 병목 지점 및 3대 리팩토링 대상 영역(Speculative Decoding, Structured Outputs, 핫스왑 세션 고도화)이 도출되어야 한다.
2. **Given** 분석된 리팩토링 명세가 주어졌을 때, **When** 테스트 수트 검증이 이루어지면, **Then** 기존 API 하위 호환성 100% 보장 및 146+ 개 테스트 Pass 상태가 유지되어야 한다.

---

### User Story 2 - Speculative Decoding 및 구조화된 출력(Structured Output) 엔진 모듈화 (Priority: P2)

엔드포인트 사용자가 OpenAI 규격의 `response_format={"type": "json_object"}` 또는 `json_schema` 옵션을 전달했을 때, 백엔드 추론 엔진에서 스키마 기반 문법(Grammar) 가이드를 동적으로 전달하고 추론 속도를 1.5배~2배 향상시킵니다.

**Why this priority**: RAG 및 멀티에이전트 서비스 환경에서 JSON 응답의 무결성을 보장하고 응답 지연(Latency)을 낮추기 위함입니다.

---

### Edge Cases

- 소형 VRAM(11GB) 환경에서 Draft 모델 추가 탑재 시 VRAM OOM 방지 제한 logic
- 구형 패키지 버전과의 호환성 유지

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 2026년 7월 최신 기술 트렌드 기반 프로젝트 분석 리포트 및 리팩토링 설계(`spec.md`, `research.md`, `plan.md`) 완료
- **DoD-002**: Speculative Decoding & Structured Output 스키마 연동 명세 도출
- **DoD-003**: 100% 회귀 테스트 통과 및 하위 호환성 검증

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (2026 최신 기술 스택 기반 코드베이스 리팩토링 분석)**: `llama.cpp` 최신 가속 기술 및 Speculative Decoding, Structured Output 지원 항목을 조사하고 파이프라인 적용 구조를 분석해야 한다.
- **FR-002 (OpenAI 호환 Structured Output 규격 반영)**: `POST /v1/chat/completions` 요청 시 `response_format` 파라미터를 파싱하여 `llama-server` 문법 가이드로 전달하는 리팩토링 항목을 정의해야 한다.
- **FR-003 (드래프트 모델 기반 Speculative Decoding 구조 설계)**: 경량 드래프트 모델(Qwen 3.5 0.5B / Gemma 4 E2B)을 활용한 추론 가속 파이프라인 명세를 도출해야 한다.

### Key Entities

- **RefactoringAnalysisReport**: 최신 기술 기반 코드베이스 개선 분석 결과.
- **StructuredOutputSchema**: JSON Schema 기반 문법 가이드 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 2026 최신 LLM 서빙 표준 기반 3대 핵심 리팩토링 명세 완성
- **SC-002**: 기존 REST API 및 SDK 연동 100% 하위 호환 보장
- **SC-003**: 전체 146+ 개 Pytest 수트 100% 통과 보장

## Assumptions

- GTX 1080 Ti (11GB VRAM) 환경을 기준 시스템으로 하되, 드래프트 모델 추가 로드 시 VRAM 한계(11264MB)를 엄격히 준수함.
