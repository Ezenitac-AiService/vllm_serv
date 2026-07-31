# Feature Specification: vllm_serv API 예제 샘플 스크립트 작성 (sample_01 ~ sample_05)

**Feature Branch**: `063-sample-server-api-examples`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "sample_숫자.py 로, 우리 llm 서버에 어떻게 호출하는지 예시 코드를 작성하는 스펙 작성: 01. 일반 채팅 호출, 02. 모델과 파라메타 값을 바꿔가며, 03. 임베딩 모델 호출, 04. 리랭킹 모델 호출, 05. 출력 양식 지정 호출 - .legacy/ATEAM_ExtractionItem.py .legacy/BTEAM_ExtractionItem.py 같은 예제"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 독립 실행 가능한 일반 채팅 호출 예제 스크립트 (`sample_01_chat.py`) (Priority: P1) 🎯 MVP

개발자 및 신규 서비스 이용자는 간단한 파이썬 예제 코드를 직접 실행하여 vllm_serv 메인 서버(8081 포트)의 `/v1/chat/completions` API를 통해 LLM 모델과 주고받는 단기/다중 대화 호출 방법을 파악하고 실시간 응답을 확인할 수 있어야 합니다.

**Why this priority**: 가장 기본적인 LLM 서버 연동 예제로, 서버 생관 헬스체크 및 기본적인 OpenAI 규격 메시지 전달 방식을 직관적으로 제시하는 필수 기반 시나리오입니다.

**Independent Test**: `uv run python samples/sample_01_chat.py` 실행 시 8081 메인 서버로 HTTP POST 요청을 보내고 정상적인 200 OK 응답 및 텍스트 답변이 콘솔에 출력되는지 독립 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** vllm_serv 메인 서빙 프로세스(8081)가 구동 중일 때, **When** `sample_01_chat.py`를 실행하면, **Then** 표준 HTTP 메시지 형식으로 대화를 전달하고 모델 답변 결과가 출력되어야 합니다.
2. **Given** 서버 연결 상태, **When** 스트리밍 옵션(`stream=False`) 기본 호출 시, **Then** 예외 없이 완료된 텍스트 응답 결과를 획득해야 합니다.

---

### User Story 2 - 동적 모델 변경 및 추론 파라미터 제어 예제 (`sample_02_model_params.py`) (Priority: P2)

개발자는 다양한 카탈로그 모델(`qwen3.5-4b`, `gemma4-12b` 등) 및 생성 인자(`temperature`, `top_p`, `max_tokens`, `stop`)를 동적으로 설정하여 서버로 전달하고 결과를 비교 검증하는 예제 스크립트를 필요로 합니다.

**Why this priority**: 다양한 서비스 요구사항에 맞춰 답변의 창의성, 토큰 수 제한, 특정 정지 문자열 제어 등 세부 파라미터를 조절하는 방법을 명확히 전달해야 합니다.

**Independent Test**: `uv run python samples/sample_02_model_params.py` 실행 시 지정된 파라미터 조합별로 성공적인 응답을 반환하는지 독립 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 모델 ID 및 파라미터 패키지가 설정되어 있을 때, **When** `sample_02_model_params.py`가 서로 다른 파라미터 셋으로 연속 호출되면, **Then** 각 설정에 맞는 응답 데이터 구조가 정상 반환되어야 합니다.

---

### User Story 3 - 임베딩 및 리랭킹 보조 모델 전용 호출 예제 (`sample_03_embedding.py`, `sample_04_reranking.py`) (Priority: P3)

RAG 개발자 및 데이터 분석가는 BGE M3 임베딩 모델(8090 포트)과 BGE Reranker v2 M3 Cross-Encoder 모델(8091 포트)로 직접 벡터 생성 및 문맥 재정렬 API를 호출하는 예제 코드를 필요로 합니다.

**Why this priority**: RAG 파이프라인 구축 시 필수적인 보조 모델 서빙 엔드포인트 호출 규격과 베터/스코어 응답 파싱 방법을 제시합니다.

**Independent Test**: `uv run python samples/sample_03_embedding.py` 및 `sample_04_reranking.py` 실행 시 각각 8090/8091 전용 포트로 요청을 전달하여 1024차원 벡터 및 문서 관련도 스코어를 산출하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** bge-m3 임베딩 서버가 8090 포트에 구동 중일 때, **When** `sample_03_embedding.py`를 실행하면, **Then** `/v1/embeddings` 엔드포인트를 통해 벡터 수치 배열을 획득해야 합니다.
2. **Given** bge-reranker-v2-m3 서빙이 8091 포트에 구동 중일 때, **When** `sample_04_reranking.py`를 실행하면, **Then** 쿼리 및 문서 집합에 대한 재정렬 스코어 또는 연동 결과를 반환받아야 합니다.

---

### User Story 4 - Pydantic 기반 구조화된 출력 규격 추출 예제 (`sample_05_structured_output.py`) (Priority: P4)

에이전트 개발자는 `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py`에 정의된 도메인 데이터 스키마(주식 분석, 리뷰 감성 추출 등)를 활용하여 LLM 응답을 엄격한 JSON/Pydantic 스키마로 파싱하는 구조화된 출력 예제를 필요로 합니다.

**Why this priority**: 레거시 스키마 정의를 재활용하여 JSON Schema 지시어 및 Pydantic 객체 검증을 통한 구조화 데이터 추출 파이프라인의 실무 예시를 제공합니다.

**Independent Test**: `uv run python samples/sample_05_structured_output.py` 실행 시 ATEAM/BTEAM 스키마 형태의 검증된 JSON 출력과 Pydantic 인스턴스 파싱이 성공하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** ATEAM 및 BTEAM 추출 스키마 파일이 존재할 때, **When** `sample_05_structured_output.py`에서 스키마 기반 시스템 프롬프트를 전달하고 호출하면, **Then** 규격에 맞는 Pydantic 파싱 결과 객체를 얻어야 합니다.

---

### Edge Cases

- 서버 포트(8081, 8090, 8091)에 인스턴스가 구동 중이지 않거나 연결 거부(`ERR_CONNECTION_REFUSED`) 시 예제 스크립트가 명확한 사용법 및 오류 메시지를 안내하는가?
- 외부 라이브러리(`httpx`, `pydantic`) 의존성이 설치되지 않은 환경에서 예제 코드 실행 시 가상환경 표준 실행 명령어(`uv run python samples/sample_xx.py`) 안내가 되어 있는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `samples/` 디렉터리에 `sample_01_chat.py`, `sample_02_model_params.py`, `sample_03_embedding.py`, `sample_04_reranking.py`, `sample_05_structured_output.py` 총 5종의 예제 파일 작성 완료
- **DoD-002**: 작성된 5개 예제 파일 모두 주석 및 문서화가 한국어로 작성되어 있고 독립 실행 시 예외 없이 성공
- **DoD-003**: `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py` 스키마 규격을 `sample_05_structured_output.py`에서 정상 임포트 및 활용
- **DoD-004**: 단위 및 통합 검증 스크립트(`uv run pytest`) 및 예제 파일 실행 검증 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `samples/sample_01_chat.py` 스크립트를 통해 메인 LLM 서버(8081 포트 `/v1/chat/completions`) 기본 대화 호출 표준 코드를 제공해야 합니다.
- **FR-002**: 시스템은 `samples/sample_02_model_params.py` 스크립트를 통해 `temperature`, `top_p`, `max_tokens`, `stop` 등의 동적 생성 인자 변경 및 다중 모델 선택 예제를 제공해야 합니다.
- **FR-003**: 시스템은 `samples/sample_03_embedding.py` 스크립트를 통해 BGE M3 모델(8090 포트 `/v1/embeddings`) 벡터 생성 예제를 제공해야 합니다.
- **FR-004**: 시스템은 `samples/sample_04_reranking.py` 스크립트를 통해 BGE Reranker v2 M3 모델(8091 포트 `/v1/embeddings` 및 `/rerank`) 문맥 관련도 추출 예제를 제공해야 합니다.
- **FR-005**: 시스템은 `samples/sample_05_structured_output.py` 스크립트를 통해 `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py`에 정의된 스키마 기반 구조화 데이터(JSON Schema/Pydantic) 추출 예제를 제공해야 합니다.
- **FR-006**: 모든 예제 코드 스크립트는 `uv run python samples/sample_숫자.py` 단일 명령으로 외부 복잡한 설정 없이 로컬 가상환경에서 실행 가능해야 합니다.

### Key Entities

- **Sample Script Suite**: vllm_serv 5대 대표 호출 시나리오(`sample_01_chat.py` ~ `sample_05_structured_output.py`)를 담은 파이썬 예제 코드 모음
- **Legacy Extraction Item Schema**: `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py`에 정의된 정밀 추출용 Pydantic 데이터 모델 클래스

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 5개 예제 파일(`sample_01` ~ `sample_05`) 실행 시 로컬 vllm_serv 서버 응답 성공률 100% (오류 발생 0건)
- **SC-002**: 신규 개발자가 스크립트 주석만 읽고도 3분 이내에 원하는 API 엔드포인트 호출 코드 작성 가능 (코드 가독성 및 한국어 주석 충실도 100%)
- **SC-003**: ATEAM/BTEAM 정밀 스키마 기반 구조화된 파싱 데이터의 파싱 성공률 100%

## Assumptions

- vllm_serv 개발 서버가 로컬 기본 포트(8081: LLM, 8090: Embedding, 8091: Reranker)에서 구동 중임.
- 파이썬 3.11+ 가상환경에 `httpx`, `pydantic` 패키지가 설치되어 있음 (`uv` 기반 실행).
- `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py` 파일의 기존 스키마 정의를 수정 없이 모듈로 가용함.
