# Feature Specification: `llama-server` 네이티브 바이너리 경로 바인딩 및 `/v1/rerank` 404 근본 해결 (`081-fix-reranker-binary-path-resolution`)

**Feature Directory**: [`specs/081-fix-reranker-binary-path-resolution`](file:///home/dev/storage/vllm_serv/specs/081-fix-reranker-binary-path-resolution)  
**Created**: 2026-08-03  
**Status**: Draft  

---

## 1. Overview & Business Value

`vllm_serv` 서버 구동 시 Reranker 모델(`bge-reranker-v2-m3`) 호출 시 404 Not Found가 발생하는 근본 원인인 **`llama-server` 네이티브 바이너리 경로 미감지 및 파이썬 모듈 폴백(`llama_cpp.server`) 문제**를 해결합니다.

### 근본 원인 (실측 및 바이너리 검증 증거)

1. **`llama-server` 후보 경로 누락**: `ProcessManager.verify_and_build_llama_server()`는 `["llama-server", "llama-cpp-server", "/usr/local/bin/llama-server", "/usr/bin/llama-server"]` 경로만 검색하지만, 해당 시스템의 네이티브 C++ 바이너리는 `/usr/local/lib/ollama/llama-server`에 존재합니다.
2. **`llama_cpp.server` 파이썬 폴백의 리랭킹 기능 미지원**: 네이티브 바이너리를 탐지하지 못해 파이썬 모듈(`python -m llama_cpp.server`)로 폴백할 경우, 파이썬 서버는 `--reranking` 및 `/v1/rerank` 엔드포인트를 지원하지 않아 포트 8091 백엔드가 `/v1/rerank` 요청에 대해 404 Not Found를 반환합니다.
3. **네이티브 바이너리 감지 시 정상 동작 실측 확인**: `/usr/local/lib/ollama/llama-server` 바이너리로 8091 포트에서 `--reranking --embedding` 옵션을 실행하면 `POST http://127.0.0.1:8091/v1/rerank` 요청이 HTTP 200 OK와 올바른 relevance_score 결과를 반환합니다.

---

## 2. User Personas & Scenarios

- **Persona**: AI 애플리케이션 개발자 / RAG 파이프라인 운영자
- **Scenario**:
  1. 관리자가 `./start_server.sh`로 서버 구동 후 `sample_04_reranking.py`를 실행할 때, 보조 모델이 네이티브 `llama-server` 바이너리로 탐지 및 실행되어 `/v1/rerank` 엔드포인트에서 정상 HTTP 200 OK 응답을 수신합니다.

---

### User Story 1 - `llama-server` 네이티브 바이너리 경로 탐지 확장 (Priority: P1)

`ProcessManager.verify_and_build_llama_server()`의 탐지 대상 경로에 `/usr/local/lib/ollama/llama-server` 및 추가 표준 시스템 경로를 등록하여 네이티브 C++ 바이너리가 우선적으로 사용되도록 해야 합니다.

**Why this priority**: 파이썬 폴백 모듈은 리랭킹 엔드포인트를 지원하지 않으므로 네이티브 바이너리 바인딩이 필수적입니다.

**Independent Test**: `verify_and_build_llama_server()` 실행 결과 `build_source`가 `PYTHON_MODULE_FALLBACK`이 아닌 네이티브 경로로 감지되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 시스템에 `/usr/local/lib/ollama/llama-server` 바이너리가 존재할 때, **When** `ProcessManager.verify_and_build_llama_server()`를 호출하면, **Then** `PYTHON_MODULE_FALLBACK`이 아닌 네이티브 바이너리 경로를 탐지하여 반환합니다.
2. **Given** 네이티브 `llama-server` 바이너리로 Reranker 백엔드가 실행될 때, **When** `POST /v1/rerank` 요청이 전송되면, **Then** HTTP 200 OK와 relevance score 결과를 정상 수신합니다.

---

## 3. Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `ProcessManager`가 `/usr/local/lib/ollama/llama-server`를 포함한 네이티브 바이너리 경로를 정상 감지해야 함.
- **DoD-002**: `sample_04_reranking.py` 실행 시 404 Not Found 에러 0건 및 200 OK 성공 응답 수신.
- **DoD-003**: 단위 및 통합 테스트 작성 및 통과.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (네이티브 바이너리 경로 탐지 확장)**: `src/core/process_manager.py`의 `verify_and_build_llama_server()` 탐지 목록에 `/usr/local/lib/ollama/llama-server`, `/opt/ollama/lib/ollama/llama-server` 등 추가 시스템 바이너리 경로를 등록해야 한다.
- **FR-002 (Reranker 바이너리 바인딩 검증)**: Reranker 프로세스 spawn 시 네이티브 `llama-server` 바이너리를 사용하여 `--reranking --embedding` 옵션이 적용되도록 보장해야 한다.

---

## 5. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `sample_04_reranking.py` 호출 시 404 Not Found 에러 발생 건수 0건.
- **SC-002**: `/v1/rerank` 호출 성공률 100% (HTTP 200 OK).

---

## 6. Assumptions

- 시스템 내 `/usr/local/lib/ollama/llama-server` 바이너리가 설치되어 있습니다.
- 환경 변수나 설정 없이 기본 탐지 경로 확만으로 네이티브 바이너리를 탐지할 수 있습니다.
