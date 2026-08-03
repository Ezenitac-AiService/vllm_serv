# Feature Specification: Chat Endpoint 503 Fix & Llama Server Binary Resolution Refactoring

**Feature Branch**: `082-fix-chat-endpoint-503`

**Created**: 2026-08-03

**Status**: Draft

**Input**: User description: "방금 전 스펙(081-fix-reranker-binary-path-resolution)에 의해서, 개발 서버에서 조차 문제가 생겼음. 채팅 호출 엔드포인트(/v1/chat/completions)가 응답 안함 (503 Service Unavailable)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - OpenAI 규격 채팅 호출 엔드포인트(/v1/chat/completions) 정상 응답 회복 (Priority: P1)

개발자 및 외부 클라이언트가 `/v1/chat/completions` 엔드포인트로 HTTP POST 요청을 보낼 때, 503 Service Unavailable 오류 없이 정상적으로 LLM 인퍼런스 응답(200 OK)을 받아볼 수 있어야 합니다.

**Why this priority**: 메인 대화 API가 503으로 마비되어 서버 전체의 핵심 서빙 기능이 작동하지 않는 심각한 회귀 오류이므로 최우선 해결(P1) 대상입니다.

**Independent Test**: `uv run samples/sample_01_chat.py` 또는 `curl http://127.0.0.1:8081/v1/chat/completions` 호출 시 200 OK와 올바른 JSON 응답을 확인합니다.

**Acceptance Scenarios**:

1. **Given** vllm_serv 서버 데몬이 구동된 상태에서, **When** 클라이언트가 `/v1/chat/completions`로 유효한 대화 요청을 전송하면, **Then** 503 Service Unavailable 오류 대신 200 OK와 함께 LLM 생성 텍스트가 정상 반환되어야 합니다.
2. **Given** 기본 모델 `qwen3.5-4b` 서빙 상태에서, **When** `/health` 및 `/v1/models` 엔드포인트를 호출하고 이어 대화 요청을 보내면, **Then** 모든 엔드포인트가 정합성 있게 200 OK를 응답해야 합니다.

---

### User Story 2 - ProcessManager의 안전한 C++ llama-server 바이너리 경로 탐지 및 스탠드얼론 실행 검증 (Priority: P2)

`ProcessManager.verify_and_build_llama_server()`가 호스트 환경의 바이너리를 탐지할 때, 올라마 내장 단독 실행 불가 라이브러리(`/usr/local/lib/ollama/llama-server` 등)를 탐지 대상에서 제외하거나 실행 가능성을 사전 검증하여 정상적인 `llama-server` 바이너리만 채택하도록 개선합니다.

**Why this priority**: 부적절한 호스트 바이너리 오탐지가 `llama-server` 프로세스 무한 크래시 및 503 오류의 근본 원인이므로, 재발 방지를 위한 바이너리 탐지 강화가 필수적입니다.

**Independent Test**: `uv run pytest tests/unit/test_process_manager_binary_path.py` 실행 시 Ollama 라이브러리 경로가 오탐지되지 않음을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 호스트 환경에 `/usr/local/lib/ollama/llama-server` 파일이 존재하더라도, **When** `ProcessManager.verify_and_build_llama_server()`를 호출하면, **Then** 독립 실행 불가능한 Ollama 내장 경로 대신 검증된 스탠드얼론 바이너리 또는 로컬 `.bin/llama-server` 또는 Python 모듈 폴백을 채택해야 합니다.
2. **Given** 올바른 `llama-server` 바이너리가 선정되면, **When** `llama_manager`가 백엔드 인퍼런스 서버를 구동하면, **Then** 포트 8089에서 프로세스가 크래시 없이 즉시 READY 상태에 진입해야 합니다.

---

### Edge Cases

- 호스트에 독립 실행 가능한 `llama-server` 바이너리가 전혀 존재하지 않는 경우: 로컬 CMake 빌드 또는 Python `llama_cpp.server` 모듈 폴백이 안전하게 가동되어야 함.
- 보조 모델(Reranker, Embedding) 서빙 시 포트 8090/8091 인스턴스가 실패하더라도 메인 LLM 대화 서빙(포트 8089)이 상호 차단되거나 영향받지 않아야 함.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `uv run samples/sample_01_chat.py` 실행 시 503 오류 없이 200 OK 및 LLM 대화 응답 정상 출력 확인.
- **DoD-002**: `uv run scripts/diagnose_server_health.py` 진단 도구 실행 시 `/v1/chat/completions` 엔드포인트 상태가 `✅ OPEN / 200 OK`로 표기됨.
- **DoD-003**: `ProcessManager.verify_and_build_llama_server()` 단위 테스트 추가 및 통과 (`tests/unit/test_process_manager_binary_path.py`).
- **DoD-004**: 헌법 VII조에 따른 전체 테스트 수트(`uv run pytest`) 100% 그린 패스.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `ProcessManager.verify_and_build_llama_server()` 바이너리 탐지 시 독립 실행 불가능한 Ollama 내장 라이브러리 경로(`/usr/local/lib/ollama/llama-server`, `/opt/ollama/lib/ollama/llama-server` 등)를 탐지 우선순위에서 제외하거나 무효화해야 합니다.
- **FR-002**: 시스템은 선정된 `llama-server` 바이너리가 실제로 정상 실행 가능한지(예: `--help` 헬스체크 또는 검증된 스탠드얼론 경로) 확인한 후 서빙 프로세스를 스폰해야 합니다.
- **FR-003**: `llama_manager`는 포트 8089의 메인 백엔드 인퍼런스 엔진이 정상 구동되어 `is_ready()`가 True가 될 때까지 503 가드를 유지하되, 백엔드 구동 완료 시 즉시 200 OK로 인퍼런스 요청을 역방향 프록싱해야 합니다.
- **FR-004**: 보조 모델 관리자(`AuxiliaryManager`)는 리랭커/임베딩 프로세스의 재시도 과정에서 메인 LLM 인퍼런스 프로세스(포트 8089)를 SIGTERM으로 오정리하지 않도록 격리 조치를 준수해야 합니다.
- **FR-005**: 헌법 II조 및 III조(Zero Mock, Real Integration)를 준수하여, 모든 503 해결 검증은 하드코딩된 더미 응답이 아닌 실제 C++ 백엔드 인퍼런스 엔진 연동 통과로 증명해야 합니다.

### Key Entities

- **LlamaServerBinaryInfo**: `ProcessManager`가 탐지한 `llama-server` 바이너리의 절대 경로, CUDA 가속 활성화 여부 및 빌드 출처 정보를 보관하는 데이터 구조.
- **LlamaManager**: 메인 LLM 모델(`qwen3.5-4b` 등)의 백엔드 C++ 인퍼런스 프로세스(포트 8089) 구동 및 VRAM 오프로드 생명주기를 관리하는 싱글톤 객체.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `/v1/chat/completions` HTTP POST 요청 시 503 오류 발생률 0% 달성 및 평균 응답 개시 시간(TTFT) 정상 범위 수렴.
- **SC-002**: `uv run samples/sample_01_chat.py` E2E 샘플 스크립트 100% 성공적 실행.
- **SC-003**: 전체 회귀 테스트 수트 `uv run pytest` 통과율 100%.

## Assumptions

- 개발 서버의 NVIDIA GTX 1080 Ti (11GB VRAM) 하드웨어 환경 및 CUDA Toolkit 12.0 빌드 조건이 유지됩니다.
- Python 가상환경 내 `llama-cpp-python` 패키지는 CUDA 지원으로 정상 컴파일되어 있으며, 모듈 폴백 서빙 능력이 보장됩니다.
