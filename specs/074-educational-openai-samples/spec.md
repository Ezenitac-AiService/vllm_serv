# Feature Specification: AI 서비스 개발자 교육용 OpenAI API 표준 샘플 코드 리팩토링

**Feature Branch**: `074-educational-openai-samples`  
**Created Date**: 2026-08-03  
**Status**: DRAFT / SPECIFICATION

---

## 1. 개요 (Overview)

본 명세서는 `vllm_serv` 프로젝트 내 `samples/` 디렉터리의 교육용 샘플 스크립트들을 **AI 서비스 개발자 양성과정(K-Digital Training) 비전공자 훈련생**을 위해 표준 OpenAI API 규격 기반의 직관적인 초급 코드로 리팩토링 및 구조화하기 위한 스펙입니다.

최근 샘플 파일들에 Pydantic 모델이나 고난도 파이썬 추상화/클래스 의존성이 과도하게 주입되어 비전공자 훈련생들의 실습 학습 곡선(Learning Curve)을 왜곡시키는 문제를 해결하고, 강사/교수/훈련생/평가자 4대 다중 페르소나의 요구사항을 모두 충족하는 교육 전용 샘플 수트를 재구축합니다.

---

## 2. 다중 페르소나 심층분석 (Multi-Persona Deep Analysis)

### 🎓 1. 강사 (Instructor) 관점
- **필요성**: Pydantic 모델 수정을 유도하거나 복잡한 래퍼 함수를 가르치는 대신, 표준 `from openai import OpenAI` 또는 파이썬 기본 HTTP 딕셔너리 포맷(`requests`/`httpx`)만으로 10분 내에 수업을 진행할 수 있어야 합니다.
- **요구사항**: 
  - 각 스크립트는 외부 커스텀 파이썬 래퍼 클래스 없이 단일 파일 또는 단순 헬퍼(`common.py`)로 완결되어야 합니다.
  - 라인별 한글 주석으로 "왜 이 파라미터가 필요한지" 명확히 설명해야 합니다.

### 🏛️ 2. 교수 (Professor) 관점
- **필요성**: OpenAI API 공식 REST 프로토콜 표준 규격과의 100% 가치 대치 및 학술적 개념 일치성이 확보되어야 합니다.
- **요구사항**:
  - `Chat Completions`, `Embeddings`, `Models Catalog`, `Reranking` 각 카테고리가 OpenAI 최신 프로토콜 명세(`model`, `messages`, `temperature`, `top_p`, `stop`, `stream`)와 1:1 대응되어야 합니다.
  - 가짜 목업(Mock)이 아닌 실제 `vllm_serv` 8081/8090/8091 백엔드 소켓 통신을 검증하는 실체적 예제여야 합니다.

### 👩‍💻 3. 훈련생 (Trainee) 관점
- **필요성**: 코드를 그대로 복사해서 자신의 로컬 개발 환경에서 실행했을 때 오류 없이 직관적인 결과가 콘솔에 명확하게 표시되어야 합니다.
- **요구사항**:
  - 난해한 Pydantic 타입 힌팅 및 고난도 데코레이터를 전면 제거하고 직관적인 파이썬 딕셔너리(`dict`) 구조를 사용합니다.
  - 터미널 출력 결과에 생성된 답변, 사용 토큰 수, 완료 사유가 시각적으로 친절하게 표기되어야 합니다.

### 📋 4. 훈련기관 평가자 (Evaluator) 관점
- **필요성**: K-Digital Training / NCS AI 서비스 개발 과정의 품질 평가지표(훈련생 이수율, 산업체 적용 가능성, 표준 API 준수율)에 부합해야 합니다.
- **요구사항**:
  - 글로벌 AI 산업 표준인 OpenAI API 규격 연동 능력을 객관적으로 증명할 수 있는 표준화된 교육용 아티팩트 체계를 갖추어야 합니다.

---

## 3. 사용자 시나리오 & 테스팅 (User Scenarios)

### Scenario 1: 비전공자 훈련생의 첫 대화 API 호출 (MVP)
- **Given**: 훈련생이 `vllm_serv` 서버가 구동 중인 환경에서 `samples/sample_01_chat.py`를 열어본다.
- **When**: 훈련생이 `uv run python samples/sample_01_chat.py` 명령을 실행한다.
- **Then**: 복잡한 Pydantic 에러 없이 표준 `OpenAI(base_url="...")` 또는 `httpx.post()`를 통해 LLM 모델 답변 텍스트와 토큰 사용량이 콘솔에 깔끔히 출력된다.

### Scenario 2: 모델 제어 파라미터 실습 (Temperature & Stop)
- **Given**: 훈련생이 `samples/sample_02_model_params.py`를 실행한다.
- **When**: `temperature=0.0` 제어 및 `stop=["\n"]` 조기 중단 옵션을 테스트한다.
- **Then**: 파라미터 설정에 따른 LLM의 응답 변화가 직관적인 주석 설명과 함께 성공적으로 출력된다.

### Scenario 3: 임베딩 및 리랭커 서비스 경험
- **Given**: 훈련생이 `sample_03_embedding.py` 및 `sample_04_reranking.py`를 실행한다.
- **When**: 임베딩 벡터 및 검색 리랭킹 점수 반환을 요청한다.
- **Then**: 1024차원 수치 배열 및 문서 관련도 점수가 명확하게 표시된다.

---

## 4. 기능 요구사항 (Functional Requirements)

- **FR-001**: `samples/` 폴더 내 모든 예제 스크립트에서 파이덴틱(Pydantic) 모델 정의 및 복잡한 HTTP 객체 추상화를 전면 제거하고 표준 파이썬 딕셔너리(`dict`) 및 공식 `openai` SDK 파이프라인으로 전환해야 합니다.
- **FR-002**: `sample_01_chat.py`는 `from openai import OpenAI` 공식 라이브러리 방식과 기본 HTTP 호출 방식을 모두 직관적으로 시증해야 합니다.
- **FR-003**: 모든 샘플 파일 상단 및 주요 라인에 **비전공자 맞춤형 한글 설명 주석**을 100% 작성해야 합니다.
- **FR-004**: `common.py` 헬퍼는 복잡한 데이터 검증 로직 대신 서버 호스트/포트 자동 감지 및 가시성 높은 콘솔 프린터 역할로 최소화해야 합니다.
- **FR-005**: 헌법 II/III조(Zero-Mock 원칙)에 의거하여 예제 스크립트는 실제 `vllm_serv` 8081, 8090, 8091 서빙 포트와 연동되어 100% 그린으로 작동해야 합니다.

---

## 5. 성공 기준 (Success Criteria)

- **SC-001**: 비전공자 훈련생이 코드 수정 없이 `uv run python samples/sample_01_chat.py` 실행 시 100% 정상 작동 및 0건의 라이브러리 타입 에러 발생.
- **SC-002**: 강사/교수가 수업 중 코드 구조 설명 시간을 평균 50% 이상 단축 (직관적 파이썬 딕셔너리 구조 적용).
- **SC-003**: 4개 핵심 샘플 스크립트(`sample_01` ~ `sample_04`) 실행 시 OpenAI API 표준 응답 객체 키(`choices`, `usage`, `data`) 반환 성공률 100%.

---

## 6. 핵심 엔티티 & 샘플 파일 구조 (Key Entities & File Structure)

### 교육용 샘플 파일 수트 구성

```text
samples/
├── common.py                # 직관적인 서버 호스트 감지 및 한글 터미널 출력 헬퍼
├── sample_01_chat.py        # [기초] OpenAI 공식 SDK & HTTP 대화 API 호출 예제
├── sample_02_model_params.py # [응용] Temperature, Top_P, Stop 파라미터 제어 예제
├── sample_03_embedding.py   # [RAG] BGE M3 임베딩 추출 예제
├── sample_04_reranking.py   # [RAG] BGE Reranker v2 M3 문서 재순위화 예제
└── README.md                # 비전공자 훈련생용 5분 완성 실습 가이드
```
