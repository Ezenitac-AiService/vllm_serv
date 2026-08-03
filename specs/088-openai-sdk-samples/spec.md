# Feature Specification: OpenAI API 및 httpx 1:1 대칭 실습 예제 수트 작성 (`sample_01`~`06` & `openai_01`~`06` 총 12종) 및 `uv` 재현 환경 구성

**Feature Branch**: `088-openai-sdk-samples`

**Created**: 2026-08-03

**Status**: Draft

**Input**: User description: "samples 폴더의 실습 코드들을 httpx 기반(sample_01~06)과 openai api 라이브러리 기반(openai_01~06) 총 12개 파일로 1:1 동일한 구조로 구성. .venv 폴더는 포함하지 않으나 훈련생들이 samples 폴더를 전달받아 uv sync 명령어로 가상환경을 100% 즉시 복원할 수 있도록 uv 패키지/환경 설정 파일(pyproject.toml, uv.lock 등)을 완비함"

## Clarifications

### Session 2026-08-03

- Q: 서비스 플랫폼 호스트 IP (예: 192.168.0.80), 모델명, 생성 파라미터 관리 방식 → A: 스크립트 내부 하드코딩을 배제하고 `samples/config.json` 또는 `.env` 파일(및 `common.py` 동적 바인딩)을 통해 주소, 모델, 포트, 파라미터를 동적 설정하도록 구성.
- Q: 코드 구조 및 계층화 수준 → A: 훈련생 학습 편의성을 위해 난해한 객체지향 추상화 클래스(Abstract Base Class)나 복잡한 디자인 패턴을 배제하고, 직관적이고 직해 가능한 함수/동기 방식의 직관적 계층화 구조 사용.
- Q: 배치(Batch) 데이터 호출 지원 여부 및 실습 코드 포함 가능 여부 → A: vllm_serv 서버는 임베딩 데이터의 묶음(배열 형태의 `input=[...]`) 배치 요청을 완벽히 지원하며, `openai_03_embedding.py`에 다중 문장 배치 임베딩 벡터 추출 실습 시나리오를 명시적 수록.
- Q: 6번 배치 구조화된 응답(Batch Structured Output) 실습 파일 신설 요청 → A: 5번 파일(`sample_05` / `openai_05`)의 단일 데이터 처리 구조를 확장하여, 다중 입력 데이터(여러 주식 댓글/리뷰 목록)를 한 번의 요청으로 전달하고 Pydantic 배치 모델(`StockAnalysisResponse(results=[...])`)로 검증 및 일괄 파싱하는 6번 실습 파일(`sample_06_structured_output_batch.py` 및 `openai_06_structured_output_batch.py`)을 신설하여 수록.
- Q: 최종 실습 파일 구성 및 1:1 대칭 목록 → A: `sample_01`~`06` (httpx 기반 6개) 및 `openai_01`~`06` (OpenAI SDK 기반 6개) 총 12개 실습 파일로 1:1 완벽 대칭 구성.
- Q: `uv` 가상환경 복원 구성 및 `.venv` 배제 규칙 → A: `.venv` 가상환경 폴더는 번들 패키지에 생성/포함하지 않으나, 훈련생이 `samples/` 폴더를 전달받아 `uv sync` 단 한 줄의 명령어만으로 의존성 가상환경을 100% 즉시 자동 복원할 수 있도록 `pyproject.toml` 및 `uv.lock` 표준 패키지 설정 파일을 완전하게 통합 제공함.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 1:1 대칭 구조의 기본 대화 및 파라미터 제어 예제 제공 (Priority: P1)

훈련생은 `httpx` HTTP 저수준 호출 방식(`sample_01_chat.py`, `sample_02_model_params.py`)과 `openai` 파이썬 SDK 고수준 호출 방식(`openai_01_chat.py`, `openai_02_model_params.py`)을 1:1 대치시켜 대화형 AI 모델 호출 및 제어 파라미터(`temperature`, `stop`, `max_tokens`)를 비교 실습하고 결과를 확인할 수 있어야 합니다. 모든 설정값(서버 주소 `192.168.0.80` 등)은 하드코딩 없이 `config.json` / `.env`에서 동적으로 판독됩니다.

**Why this priority**: low-level REST API와 high-level SDK 구현 간의 구조적 차이점을 비교 습득하는 것은 AI 서비스 개발의 핵심 기초 과정입니다.

**Independent Test**: `uv run python samples/sample_01_chat.py` vs `uv run python samples/openai_01_chat.py`를 대조 실행하여 동일한 입력과 출력이 수신되는지 독립 검증합니다.

**Acceptance Scenarios**:

1. **Given** vllm_serv 메인 서빙 데몬이 서비스 플랫폼(`192.168.0.80` 등)에서 가동 중일 때, **When** `sample_01_chat.py` 및 `openai_01_chat.py`를 실행하면, **Then** 두 방식 모두 동적 로드된 호스트 주소로 서버와 통신하고 동일한 포맷의 AI 답변 결과를 출력한다.
2. **Given** vllm_serv 메인 서빙 데몬이 가동 중일 때, **When** `sample_02_model_params.py` 및 `openai_02_model_params.py`를 실행하면, **Then** `temperature=0.0` 제어 및 `stop=["\n"]` 조기 중단 동작이 동일하게 수행된다.

---

### User Story 2 - 1:1 대칭 단일/배치 임베딩 및 Rerank 문서 재순위화 예제 제공 (Priority: P2)

훈련생은 텍스트 임베딩 수치 벡터 추출(`sample_03_embedding.py` vs `openai_03_embedding.py`) 및 BGE Reranker v2 M3 문서 관련도 재순위화(`sample_04_reranking.py` vs `openai_04_reranking.py`)를 단일 및 배치(Batch) 입력에 대해 1:1 완벽 대칭으로 비교 실습할 수 있어야 합니다.

**Why this priority**: RAG(검색 증강 생성) 핵심 컴포넌트인 임베딩 및 리랭커를 REST 및 SDK 두 가지 방식 모두로 자유자재로 다룰 수 있는 역량을 배양합니다.

**Independent Test**: `sample_03` / `openai_03` 및 `sample_04` / `openai_04`를 각각 단독 실행하여 동일한 1024차원 수치 벡터 및 관련도 점수가 출력되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** BGE M3 임베딩 데몬이 가동 중일 때, **When** `sample_03` 또는 `openai_03`을 실행하면, **Then** 단일 및 다중 문장 배치(`input=[...]`)에 대한 1024차원 수치 벡터 묶음이 수신된다.
2. **Given** Reranker 데몬이 가동 중일 때, **When** `sample_04` 또는 `openai_04`를 실행하면, **Then** 질문과 후보 문서 간의 의미적 관련도 점수(Relevance Score) 및 재정렬 순위가 수신된다.

---

### User Story 3 - 1:1 대칭 단일 및 배치 Pydantic 구조화 출력 예제 제공 (Priority: P3)

훈련생은 Pydantic 스키마 기반 구조화된 출력(Structured Output)의 단일 데이터 처리(`sample_05_structured_output.py` vs `openai_05_structured_output.py`) 및 다중 비정형 데이터 일괄 배치 처리(`sample_06_structured_output_batch.py` vs `openai_06_structured_output_batch.py`)를 1:1 대칭 코드로 실습할 수 있어야 합니다.

**Why this priority**: 실무 데이터 파이프라인에서 필수적인 비정형 텍스트 묶음(댓글/리뷰 등)의 일괄 JSON 구조화 및 타입 파싱 기법을 완벽 습득합니다.

**Independent Test**: `sample_05` / `openai_05` 및 `sample_06` / `openai_06`을 각각 실행하여 단일 및 배치 Pydantic 파싱 결과를 비교 검증합니다.

**Acceptance Scenarios**:

1. **Given** vllm_serv 메인 서빙 데몬이 가동 중일 때, **When** `sample_05` / `openai_05`를 실행하면, **Then** 단일 원문 문장이 Pydantic `StockAnalysisResponse` 모델로 정밀 파싱된다.
2. **Given** vllm_serv 메인 서빙 데몬이 가동 중일 때, **When** `sample_06` / `openai_06`을 실행하면, **Then** 3개 이상의 다중 원문 문장이 한 번의 요청으로 전달되어 Pydantic `results` 배열 객체 목록으로 일괄 검증 및 파싱된다.

---

### User Story 4 - 훈련생 `uv sync` 가상환경 즉시 복원 환경 제공 (Priority: P1)

훈련생이 배포용 `samples/` 폴더를 전달받았을 때, 물리적인 `.venv` 폴더 없이도 폴더 내에서 `uv sync` 명령 단 한 번으로 필요한 모든 의존성 패키지(httpx, openai, pydantic 등)가 가상환경으로 100% 즉시 원복되어 실행 가능해야 합니다.

**Why this priority**: 훈련생의 컴퓨터 환경 차이로 인한 가상환경 꼬임 에러를 방지하고 표준 `uv` 가상환경 복원 메커니즘을 경험시킵니다.

**Independent Test**: `.venv` 폴더가 존재하지 않는 클린 상태에서 `uv sync` 실행 후 `uv run python samples/openai_01_chat.py` 실행이 즉시 성공하는지 독립 검증합니다.

**Acceptance Scenarios**:

1. **Given** `.venv` 가상환경 폴더가 존재하지 않을 때, **When** 훈련생이 `uv sync` 명령을 실행하면, **Then** `pyproject.toml` 및 `uv.lock` 기반으로 가상환경이 자동 생성되고 모든 실습 스크립트가 실행 가능 상태가 된다.

---

### Edge Cases

- **.venv 폴더 포함 방지**: 버전 관리 및 배포 팩 생성 시 대용량 `.venv` 바이너리 폴더는 `.gitignore` 및 패키징 스크립트에 의해 완전히 배제되어야 합니다.
- **uv 미설치 시스템**: 훈련생 컴퓨터에 `uv`가 없을 경우 `pip install uv` 또는 안내 메시지를 표시하여 손쉽게 원클릭 설치 가능하도록 구성해야 합니다.
- **서버 미구동 및 설정 오류**: 서버 미구동 시 `common.check_server_health` 친절 메시지 출력 및 `config.json` 미존재 시 로컬/플랫폼 IP 자동 폴백(Fallback) 유지.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `samples/` 폴더 내에 httpx 기반 6개 (`sample_01_chat.py` ~ `sample_06_structured_output_batch.py`)와 OpenAI SDK 기반 6개 (`openai_01_chat.py` ~ `openai_06_structured_output_batch.py`) 총 12개 실습 파일이 1:1 대칭 구조로 완비된다.
- **DoD-002**: `samples/` 폴더 또는 루트에 `pyproject.toml` 및 `uv.lock` 파일이 완비되어 `.venv` 폴더 없이도 `uv sync` 명령으로 가상환경이 100% 복원된다.
- **DoD-003**: 12개 모든 실습 파일의 서버 IP, 포트, 모델명, 생성 파라미터는 하드코딩 없이 `config.json` 또는 `.env`에서 동적으로 로드된다.
- **DoD-004**: `sample_06` 및 `openai_06` 실습 파일은 다중 비정형 데이터에 대한 배치(Batch) Pydantic 구조화 출력을 일괄 처리한다.
- **DoD-005**: `uv run python samples/sample_xx_xxx.py` 및 `uv run python samples/openai_xx_xxx.py` 명령으로 12개 스크립트 전수가 오류 없이 통과함을 실체적으로 검증한다.
- **DoD-006**: `samples/README.md` 가이드 문서에 12개 실습 파일에 대한 1:1 대치 표 및 `uv sync` 가상환경 복원 실행 명령어가 업데이트된다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템(samples/)은 httpx 기반 6종(`sample_01`~`06`)과 OpenAI SDK 기반 6종(`openai_01`~`06`) 총 12종의 1:1 대칭 표준 실습 스크립트를 제공해야 합니다.
- **FR-002**: `sample_01_chat.py` & `openai_01_chat.py`는 일반 대화 통신을 1:1 비교 실습할 수 있도록 구성되어야 합니다.
- **FR-003**: `sample_02_model_params.py` & `openai_02_model_params.py`는 `temperature`, `stop`, `max_tokens` 매개변수 제어를 1:1 비교 실습할 수 있어야 합니다.
- **FR-004**: `sample_03_embedding.py` & `openai_03_embedding.py`는 단일/배치(Batch, 다중 문장) 1024차원 수치 임베딩 벡터 추출을 1:1 비교 실습할 수 있어야 합니다.
- **FR-005**: `sample_04_reranking.py` & `openai_04_reranking.py`는 BGE Reranker v2 M3 문서 관련도 점수 측정 및 재순위화를 1:1 비교 실습할 수 있어야 합니다.
- **FR-006**: `sample_05_structured_output.py` & `openai_05_structured_output.py`는 Pydantic 스키마 기반 단일 구조화 출력을 1:1 비교 실습할 수 있어야 합니다.
- **FR-007**: `sample_06_structured_output_batch.py` & `openai_06_structured_output_batch.py`는 다중 원문 데이터 묶음을 한 번에 전달받아 Pydantic `results` 배열 객체 목록으로 일괄 검증/파싱하는 배치 구조화 출력을 1:1 비교 실습할 수 있어야 합니다.
- **FR-008**: `.venv` 폴더를 포함하지 않되, 훈련생이 `samples/` 폴더를 전달받아 `uv sync` 명령어 하나로 모든 패키지 가상환경을 100% 동일하게 복원할 수 있도록 `pyproject.toml` 및 `uv.lock` 패키지 명세를 포함해야 합니다.
- **FR-009**: 12개 스크립트 전수의 서버 IP 주소(서비스 플랫폼 IP `192.168.0.80` 등), 포트, 모델명, 생성 파라미터는 스크립트 내 하드코딩 없이 `config.json` 또는 `.env` 설정 파일에서 동적으로 읽어와야 합니다.
- **FR-010**: 모든 스크립트는 난해한 추상화 클래스를 배제하고 비전공자/초급 훈련생이 3분 내 직해 가능한 단일 파일 순수 함수 계층 구조를 준수해야 합니다.

### Key Entities *(include if feature involves data)*

- **uv Package Lock Specification**: `pyproject.toml` 및 `uv.lock` 기반 가상환경 복원 명세 데이터.
- **1:1 Paired Sample Suite**: 6쌍(총 12개)의 httpx REST API 버전과 OpenAI SDK 버전 실습 파일 묶음.
- **Configuration Settings**: `config.json` / `.env`에서 읽어온 서버 IP (`server_host`), 메인 포트(`main_port`), 임베딩 포트(`embedding_port`), 모델명(`model_name`), 파라미터 딕셔너리.
- **Structured Output Pydantic Model (Single & Batch)**: 단일 및 배치 분석 결과를 수담는 `StockAnalysisResponse` 및 `StockCommentItem`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 12개 `sample_xx_xxx.py` 및 `openai_xx_xxx.py` 스크립트 실행 시 100% 정상 통신 및 동일 입출력 포맷 수신이 성공해야 합니다.
- **SC-002**: `.venv` 폴더가 없는 상태에서 `uv sync` 실행 시 10초 이내에 가상환경이 100% 복원되어야 합니다.
- **SC-003**: `config.json` 또는 `.env` 파일의 IP(예: `192.168.0.80`)나 모델 변경 시, 12개 파일 전수가 스크립트 수정 없이 즉시 동적 반영되어야 합니다.
- **SC-004**: `sample_06` 및 `openai_06` 배치 구조화 응답 실행 시 3개 이상의 다중 원문 데이터에 대한 Pydantic 파싱 검증이 100% 성공해야 합니다.
- **SC-005**: 모든 스크립트는 복잡한 추상화 클래스 없이 100줄 이내의 명확한 단일 파일 단위로 작성되어 훈련생 독해 시간이 3분 이내로 수렴해야 합니다.

## Assumptions

- **uv Package Manager Environment**: 훈련생 환경에 `uv`가 기본 설치되어 있거나 `pip install uv`로 즉시 사용 가능함.
- **Zero .venv Distribution**: Git 관리 및 배포 패키징 시 `.venv` 디렉토리는 오염 방지를 위해 절대 포함하지 않으며 `uv sync`로 복원하는 표준 원칙 준수.
- **Existing Utility & Config**: `samples/config.json` 또는 `samples/common.py`를 활용하여 동적 IP(`192.168.0.80` 등) 및 설정 파싱 지원.
- **API Key Standard**: vllm_serv 로컬/원격 서빙 데몬은 API Key 검증이 비활성화되어 있거나 더미 키(`EMPTY`)를 지원함.
