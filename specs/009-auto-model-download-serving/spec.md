# Feature Specification: 자동 모델 다운로드 및 동적 서빙 프로세스 실행 관리 (Automatic Model Download & Dynamic Serving Automation)

**Feature Branch**: `009-auto-model-download-serving`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "모델 다운로드하고 로드하는 것도 구현이 안되어있는거야?" (자동 GGUF 모델 다운로드 및 서빙 프로세스 동적 로드/스위칭 자동화)

## Clarifications

### Session 2026-07-29

- Q: 모델 파일 미존재 시 자동 다운로드 출처 및 방식 → A: HuggingFace GGUF 공식 리포지토리(`huggingface_hub` / `hf_hub_download`)를 통해 분할 다운로드 및 이어받기 지원
- Q: GPU VRAM 제한(11GB) 초과 모델 및 동적 스위칭 처리 방식 → A: 이전 서빙 모델 프로세스를 `SIGTERM` ➔ `SIGKILL`로 안전 종료 후 VRAM 점유 완전 해제 확인 후 신규 모델 프로세스 로드
- Q: 자동 다운로드 시 사용자 UI/CLI 시각화 → A: 프로그레스 바(Progress bar) 및 다운로드 속도/남은 시간 표시

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 미존재 GGUF 모델 자동 다운로드 및 검증 (Priority: P1) 🎯 MVP

시스템 엔지니어 및 테스터는 로컬 `models/` 디렉토리에 원하는 서빙 모델(Qwen 3.5 2B/4B/9B 및 Gemma 4 E2B/E4B/12B)의 GGUF 가중치가 존재하지 않는 경우, 수동 다운로드 과정 없이 HuggingFace Hub로부터 정밀도별 GGUF 파일 및 CLIP 프로젝터 파일(Gemma 4 멀티모달용)을 자동 다운로드받을 수 있어야 합니다.

**Why this priority**: 사용자가 모델 가중치 파일 수동 다운로드 없이 단일 명령어로 벤치마크 및 로컬 LLM 서빙을 즉각 시작할 수 있도록 하기 위함입니다.

**Independent Test**: 모델 디렉토리가 비어있는 상태에서 다운로드 모듈을 구동했을 때, HuggingFace Hub로부터 파일이 지정 경로에 완전하게 다운로드되고 무결성이 검증되는지 독립 테스트 가능합니다.

**Acceptance Scenarios**:

1. **Given** `models/qwen3.5-2b/` 폴더에 GGUF 파일이 존재하지 않을 때, **When** 시스템에 Qwen 3.5 2B 서빙 요청이 전달되면, **Then** HuggingFace 리포지토리에서 `qwen-3.5-2b-instruct-q4_k_m.gguf` 파일이 자동 다운로드됩니다.
2. **Given** Gemma 4 멀티모달 모델 요청 시, **When** 다운로드가 시작되면, **Then** 메인 GGUF 가중치와 CLIP 프로젝터(`mmproj`) 파일이 함께 다운로드됩니다.
3. **Given** 다운로드 도중 네트워크가 중단되었다가 재개될 때, **When** 재요청이 발생하면, **Then** 이어서 다운로드(Resume)가 진행됩니다.

---

### User Story 2 - llama-server 동적 라이프사이클 관리 및 서빙 자동화 (Priority: P2)

사용자는 로컬 모델 스위칭 요청 시, 기존 실행 중인 서빙 프로세스를 안전하게 언로드하고 GPU VRAM을 즉시 해제한 후, 신규 모델 서빙 프로세스를 개설하여 HTTP OpenAI 호환 API 포트(`127.0.0.1:8081/v1`)를 준비 완료 상태로 전환받을 수 있어야 합니다.

**Why this priority**: GTX 1080 Ti 11GB VRAM 한계 내에서 6종 라인업 모델을 수동 포트 관리 없이 동적으로 스위칭 구동하기 위함입니다.

**Independent Test**: 모델 스위칭 API 호출 시 기존 프로세스 종료, VRAM 반납, 신규 프로세스 헬스체크(`/v1/models`) 정상 반환을 테스트 가능합니다.

**Acceptance Scenarios**:

1. **Given** Gemma 4 2B가 구동 중인 상태에서 Qwen 3.5 4B 로드 요청 시, **When** 스위칭 함수가 호출되면, **Then** Gemma 4 프로세스가 안전 종료되고 VRAM이 해제된 후 Qwen 3.5 4B 프로세스가 READY 상태로 전환됩니다.
2. **Given** VRAM 추정량이 11GB 한계를 초과하는 대형 모델 요청 시, **When** VRAM 검증이 수행되면, **Then** OOM 경고 에러 메시지와 함께 안전 차단됩니다.

---

### User Story 3 - 자동 다운로드 + 로드 + 3D 실측 벤치마크 원스톱 구동 (Priority: P3)

사용자는 단 한 번의 벤치마크 명령 구동으로 [미존재 모델 자동 다운로드 ➔ 실측 프로세스 로드 ➔ nvtop 실측 부하 발생 ➔ 품질 평가 ➔ 보고서 생성] 원스톱 자동화를 경험할 수 있어야 합니다.

**Why this priority**: 실제 GPU Cuda 코어 및 VRAM 실측 데이터를 사람의 개입 없이 풀 자동화하기 위함입니다.

**Acceptance Scenarios**:

1. **Given** `--auto-download` 및 `--real-inference` 플래그를 지정하여 벤치마크 구동 시, **When** 실행이 진행되면, **Then** 6종 모델이 다운로드-로드-실측추론-보고서갱신까지 자동 완수됩니다.

---

### Edge Cases

- **네트워크 연결 끊김 및 디스크 공간 부족**: 다운로드 시 404/Timeout 발생 시 서빙 에러 상태 반환 및 잔여 용량 사전 체크.
- **포맷 깨진 가중치 파일**: 다운로드 완료 후 파일 크기 및 SHA256 체크로 손상 파일 자동 재다운로드.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: HuggingFace Hub 연동 자동 모델 다운로더 모듈(`src/core/model_downloader.py`) 구현 완료.
- **DoD-002**: Qwen 3.5 3종 및 Gemma 4 3종 모델에 대한 동적 프로세스 스위치 및 HTTP 헬스체크 바인딩 구현.
- **DoD-003**: 벤치마크 스크립트에 자동 다운로드 + 실측 연동 기능 수록 및 전체 pytest 100% 통과.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `huggingface_hub` API를 통해 Qwen 3.5 및 Gemma 4 GGUF 가중치와 mmproj CLIP 가중치를 자동 다운로드하고 저장할 수 있어야 합니다.
- **FR-002**: 시스템은 다운로드 진행 상황(다운로드 속도, % 진행률, 바이트 단위 크기)을 터미널/로그에 시각화해야 합니다.
- **FR-003**: 시스템은 모델 로드 요청 시 로컬 가중치 미존재를 탐지하고, 자동 다운로드를 수행한 후 프로세스를 구동해야 합니다.
- **FR-004**: 프로세스 매니저는 기존 구동 중인 `llama-server` 프로세스를 안전하게 종료하고 GPU VRAM을 완전 해제한 후 신규 모델을 구동해야 합니다.
- **FR-005**: 벤치마크 스크립트는 원스톱 모드(`--auto-download --real-inference`) 구동 시 6개 모델에 대해 다운로드-서빙프로세스개설-실측추론-보고서 생성을 자동 수행해야 합니다.

### Key Entities

- **ModelDownloadTask**: model_id, repo_id, filename, target_path, is_completed, download_progress_pct
- **ServerProcessState**: status (UNLOADED, DOWNLOADING, LOADING, READY, ERROR), model_id, port, pid

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 모델 가중치 파일이 없는 최초 상태에서도 단 한 번의 명령어 구동으로 서빙 서버가 100% 자동 구동되어야 합니다.
- **SC-002**: 서빙 모델 스위칭 시간이 평균 5초 이내(다운로드 완료 기준)로 완료되어야 합니다.
- **SC-003**: 모든 신규 및 기존 pytest 테스트 케이스 통과율 100%를 유지해야 합니다.

## Assumptions

- 시스템 환경에 Python `huggingface_hub` 패키지가 설치되어 있거나 pip/uv로 이용 가능하다고 가정합니다.
- HuggingFace Hub 다운로드를 위한 인터넷 네트워크 연결이 확보되어 있다고 가정합니다.
