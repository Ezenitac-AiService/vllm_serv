# Feature Specification: Gemma 4 Model Loading Fix & MMProj Vision Projector Binding

**Feature Branch**: `specs/015-gemma4-model-loading-fix`

**Created**: 2026-07-29

**Status**: Approved

**Input**: User description: "gemma4 모델들 텍스트만 입력받게 하는 부분이 문제 있는거 아냐? 그 이후로 gemma4 모델 로드가 안되고 있어, 2026년 7월 최신 공식 레퍼런스, 공식 가이드, 우수 예제 등을 리서치해봐"

---

## Executive Summary & User Value

본 피처는 `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b` 모델 로딩 시 VRAM 오프로드 0/36 레이어 실패 및 헬스체크 타임아웃이 발생하던 원인을 근본 해결합니다.

**원인 분석**:
`gemma4` 하이브리드 비전-텍스트 GGUF 아키텍처는 `per_layer_token_embd.weight`, `per_layer_model_proj.weight` 등 멀티모달 임베딩 레이어를 포함합니다. `llama-server` / `llama_cpp.server` 인스턴스 개설 시 MMProj(CLIP) 프로젝터 파일(`--mmproj` / `--clip_model_path`)을 생략(Bypass)할 경우 `llama.cpp` GPU 백엔드가 CUDA 그래픽 그래프 텐서 할당을 포기하고 `0/36 layers offloaded to GPU` 상태로 폴백되어 100% VRAM 오프로드 검증 실패 및 헬스체크 타임아웃을 유발합니다.

**해결 방안**:
1. Gemma 4 카탈로그 프리셋에 바인딩된 MMProj 프로젝터 파일(`gemma-4-E2B-it-mmproj.gguf`, `gemma-4-E4B-it-mmproj.gguf`)을 필수 바인딩합니다.
2. `ProcessManager`에서 Gemma 4 모델 개설 시 MMProj 프로젝터 존재 여부를 검증하고 CLI 인자(`--mmproj` 또는 `--clip_model_path`)로 전달하여 `36/36 layers offloaded` 100% CUDA 가속 서빙을 보장합니다.
3. HuggingFace Hub 다운로더(`ModelDownloader`)가 Gemma 4 GGUF 가중치 다운로드 시 세트 MMProj 프로젝터 파일도 자동으로 함께 원스톱 받도록 구현합니다.

---

## Clarifications

### Session 2026-07-29

- Q: LLM 서버 동기/비동기 응답 및 인퍼런스 병렬 처리 여부 → A: 비동기 HTTP REST API + 단일 순차 인퍼런스 큐 (`n_seq_max=1`). HTTP 요청은 비동기/스트리밍으로 처리하되 VRAM OOM 방지를 위해 GPU 추론은 1개씩 순차 진행.

---


## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gemma 4 MMProj 결합을 통한 100% CUDA VRAM 오프로드 로딩 (Priority: P1)

**User Story**: AI 개발자 및 서비스 운영자는 Gemma 4 (E2B, E4B) 모델 로드 시 MMProj 프로젝터가 자동 결합되어 36/36 전체 레이어가 GPU VRAM에 100% 오프로드되고 헬스체크 200 OK 상태로 즉시 서비스 준비가 되길 원한다.

**Why this priority**: Gemma 4 모델 시리즈가 라이브 GPU 상에서 로드되지 않던 기존 고질 장애를 즉시 해결하는 핵심 요구사항입니다.

**Independent Test**: `uv run python scripts/benchmark_quality.py --auto-download --real` 실행 시 Gemma 4 E2B 및 E4B 모델이 36/36 layers offloaded로 정상 로드되고 헬스체크 200 OK를 리턴받아 평가 샘플 추론을 완료함을 검증.

**Acceptance Scenarios**:

1. **Given** Gemma 4 E2B/E4B 모델 로드 요청 시, **When** 로컬 디렉터리에 `.mmproj.gguf` 파일이 존재할 경우, **Then** `ProcessManager`는 MMProj 인자를 추가하여 프로세스를 개설하고 `36/36 layers offloaded to GPU` 100% VRAM 오프로드를 달성한다.
2. **Given** 벤치마크 및 라이브 인퍼런스 서버 구동 시, **When** Gemma 4 E2B/E4B 모델에 헬스체크 요청을 보낼 때, **Then** 120초 이전에 HTTP 200 OK 응답을 반환하고 `ProcessStatusEnum.READY` 상태로 전환된다.

---

### User Story 2 - HuggingFace Hub 원스톱 MMProj 프로젝터 자동 다운로드 (Priority: P1)

**User Story**: 인프라 운영자는 Gemma 4 모델 다운로드 시 메인 GGUF 가중치 파일과 짝을 이루는 MMProj 프로젝터 파일도 한 번의 명령으로 자동 다운로드되길 원한다.

**Why this priority**: MMProj 프로젝터 파일 누락으로 인한 GPU 인퍼런스 엔진 로딩 실패를 사전 차단합니다.

**Independent Test**: `ModelDownloader.download_model("gemma4-e2b")` 실행 시 메인 GGUF 및 MMProj 파일이 디렉터리에 동시 확보됨을 확인.

**Acceptance Scenarios**:

1. **Given** `ModelDownloader`가 Gemma 4 계열 모델 다운로드를 수행할 때, **When** 로컬 디렉터리에 MMProj 프로젝터가 없으면, **Then** HuggingFace Hub 릴리즈 저장소에서 MMProj 파일을 자동 다운로드하여 설치한다.

---

## Edge Cases

- Gemma 4 MMProj 파일이 훼손되거나 다운로드 실패 시: 명확한 `ModelNotFoundError` 메시지를 출력하고 `ProcessStatusEnum.ERROR`로 처리함.
- NVIDIA GTX 1080 Ti VRAM 11GB 공간 부족 시: Pre-flight VRAM estimator가 OOM을 사전 차단하고 안전하게 이전 서빙 프로세스를 유지함.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: Gemma 4 E2B 및 E4B 모델 개설 시 `36/36 layers offloaded to GPU` 100% VRAM 오프로드 성공 및 헬스체크 200 OK 달성.
- **DoD-002**: `python scripts/benchmark_quality.py --auto-download --real` 실행 시 Gemma 4 E2B, E4B, Qwen 3.5 전체 모델 순차 구동 및 품질 리포트 작성이 정상 작동함.
- **DoD-003**: `pytest` 단위/통합 테스트 수트 전체 통과.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Gemma 4 MMProj 프로젝터 필수 결합)**: `ProcessManager`는 Gemma 4 계열 모델(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`) 프로세스 스폰 시 해당 모델의 MMProj 프로젝터 파일 경로(`models/gemma4-XX/...mmproj.gguf`)를 검증하고, `--mmproj` 또는 `--clip_model_path` CLI 인자로 반드시 전달해야 한다.
- **FR-002 (Gemma 4 100% CUDA VRAM 오프로드 보장)**: Gemma 4 서빙 프로세스 실행 시 36/36 전체 레이어가 GPU VRAM에 오프로드되었음을 로그 인스펙션(`offloaded 36/36 layers to GPU`)을 통해 검증하고 READY 상태로 전환해야 한다.
- **FR-003 (원스톱 MMProj 프로젝터 자동 다운로드)**: `ModelDownloader`는 Gemma 4 카탈로그 모델 다운로드 요청 시 메인 GGUF 가중치 파일과 함께 짝을 이루는 MMProj 파일도 원스톱으로 다운로드해야 한다.
- **FR-004 (듀얼 모드 테스트 수트 최신화)**: Pytest 수트 및 `test_serving_switch.py` 테스트는 Gemma 4 MMProj 결합 및 100% VRAM 오프로드를 검증하는 테스트 케이스를 포함해야 한다.
- **FR-005 (비동기 HTTP I/O & 단일 순차 인퍼런스 큐)**: REST API 서버는 비동기(Async) / 스트리밍(SSE) 요청 처리를 지원하되, GTX 1080 Ti (11GB VRAM) 한계에 따른 OOM을 방지하기 위해 GPU 모델 추론 엔진은 단일 순차 큐(`n_seq_max=1`)로 요청을 1개씩 순차적으로 처리해야 한다.

### Key Entities

- **Gemma4ModelPreset**: Gemma 4 모델 GGUF 경로, MMProj 경로, VRAM 사용량 추정치, 챗 템플릿 정보를 정의하는 데이터 모델.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (Gemma 4 GPU VRAM 오프로드율)**: Gemma 4 E2B 및 E4B 모델 개설 시 GPU VRAM 오프로드 레이어 비중 100% (`36/36 layers`).
- **SC-002 (Gemma 4 헬스체크 성공률)**: `pytest --real` 및 라이브 서빙 시 Gemma 4 헬스체크 200 OK 성공률 100%.
- **SC-003 (품질 벤치마크 수행률)**: Gemma 4 포함 6개 모델 실측 벤치마크 구동 시 Gemma 4 모델 10개 평가 샘플 100% 추론 성공.

---

## Assumptions

- **Gemma 4 GGUF 아키텍처**: 2026년 최신 `llama.cpp` 백엔드에서 `gemma4` 아키텍처는 MMProj 프로젝터 바인딩 시 CUDA GPU 백엔드 멀티모달 그래픽 그래프 텐서를 100% 오프로드하도록 설계됨.
- **로컬 디렉터리 구조**: MMProj 파일은 각 Gemma 4 모델 디렉터리(`models/gemma4-2b/gemma-4-E2B-it-mmproj.gguf` 등)에 저장됨.
