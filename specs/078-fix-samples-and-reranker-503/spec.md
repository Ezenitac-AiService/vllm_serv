# Feature Specification: 샘플 스크립트 IP 설정 구조화 및 Reranker API 503 오류 해결 (`078-fix-samples-and-reranker-503`)

**Feature Directory**: [`specs/078-fix-samples-and-reranker-503`](file:///home/dev/storage/vllm_serv/specs/078-fix-samples-and-reranker-503)  
**Created**: 2026-08-03  
**Status**: In Review (Clarified)  

---

## 1. Overview & Business Value

개발 플랫폼 대역(`10.0.0.x`)과 서비스 플랫폼 대역(`192.168.0.x`) 등 다양한 내부망 환경에서 작동하는 샘플 교육용 스크립트(`samples/` 대역)의 IP 설정 구조를 체계화하여, 하드코딩 없이 `samples/config.json` 및 `samples/.env` 설정을 통해 호스트 주소를 유연하게 구성할 수 있도록 수정합니다. 또한 BGE Reranker v2 M3 리랭킹 요청(`/v1/rerank`) 시 발생하는 `503 Service Unavailable` 오류를 해결합니다.

`samples/common.py` 모듈이 `samples/config.json`, `samples/.env`, 환경변수(`SERVER_HOST`, `OPENAI_BASE_URL`) 설정을 최우선 파싱하도록 보장하고, 하드코딩된 특정 IP 주소를 전면 제거하며, `/v1/rerank` 및 `/v1/embeddings` 프록시 라우팅 시 온디맨드(On-Demand) 백엔드 가동 보장(`auxiliary_manager.ensure_rerank_resident()`)을 적용하여 100% 정상 서비스를 보장합니다.

---

## 2. User Personas & Scenarios

- **Persona**: 초급 AI 훈련생 / 교육생 / 애플리케이션 개발자 (내부망 클라이언트 PC 이용자)
- **Scenario**:
  1. 교육생이 개발 플랫폼 대역(`10.0.0.x`)에서 `samples/config.json`에 설정된 서버 주소로 `python samples/sample_01_chat.py`를 실행할 때, 하드코딩 없이 설정된 주소로 즉시 연결되어 AI 답변을 수신합니다.
  2. 교육생이 서비스 플랫폼 대역(`192.168.0.x`)에서 `samples/config.json`을 통해 서버 IP를 구성하고 스크립트를 실행할 때, 해당 주소로 정상 연결됩니다.
  3. 교육생이 `python samples/sample_04_reranking.py`를 실행할 때, `/v1/rerank` 요청이 503 에러 없이 8091 Reranker 백엔드 데몬의 온디맨드 준비를 거쳐 문서 재순위화 결과를 정상 반환받습니다.

---

### User Story 1 - `samples/config.json` 기반 서버 IP 설정 체계화 및 하드코딩 제거 (Priority: P1)

샘플 예제 스크립트가 코드 내 하드코딩된 IP 주소 없이 `samples/config.json`, `samples/.env`, 및 `SERVER_HOST` 환경변수 설정을 통해 대상 서버 IP를 결정하도록 체계화해야 합니다.

**Why this priority**: 플랫폼 환경(개발/서비스)이 변경되더라도 코드를 수정하지 않고 `config.json` 설정 변경만으로 모든 샘플이 정상 동작하도록 보장하는 소프트웨어 표준화 관점의 최우선 요구사항입니다.

**Independent Test**: `samples/config.json`에 명시한 주소(`http://10.0.0.41` 또는 `http://192.168.0.100`)로 `get_server_host()`가 정확히 반환하여 서버와 통신하는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** `samples/config.json`에 서버 IP(`server_host`)가 설정된 경우, **When** `sample_01_chat.py` 등 샘플 스크립트를 실행하면, **Then** `config.json`에 기재된 IP 주소를 파싱하여 8081 서버로 통신합니다.
2. **Given** 환경변수 `SERVER_HOST`가 설정된 경우, **When** `get_server_host()`를 호출하면, **Then** 환경변수 값을 최우선 적용합니다.
3. **Given** 소스코드 내 하드코딩된 후보 IP 목록, **When** 정적 코드 검사를 수행하면, **Then** 소스코드 내 하드코딩된 특정 IP 주소 주입 방식이 전면 배제되었음을 검증합니다.

---

### User Story 2 - Reranker API `/v1/rerank` 온디맨드 가동 및 503 오류 제거 (Priority: P1)

`/v1/rerank` 또는 `/v1/embeddings` 엔드포인트 요청 수신 시 백엔드 보조 데몬(8091 Reranker / 8090 Embedding)이 미가동 상태이거나 준비 중일 때, 온디맨드로 인스턴스를 자동으로 가동·대기시켜 `503 Service Unavailable` 예외를 방지하고 정상 결과를 리턴해야 합니다.

**Why this priority**: RAG 파이프라인의 핵심인 리랭킹 서비스의 가용성 및 파이프라인 신뢰성을 보장하기 위함입니다.

**Independent Test**: Reranker 데몬이 정지된 상태에서 `/v1/rerank` REST API 요청 호출 시 온디맨드로 8091 데몬이 구동되고 HTTP 200 OK와 리랭킹 결과 스코어를 정상 리턴하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 8091 Reranker 백엔드 데몬이 오프라인 상태일 때, **When** `sample_04_reranking.py` 또는 `POST /v1/rerank` 요청을 전송하면, **Then** 프록시 라우터가 `auxiliary_manager.ensure_rerank_resident()`를 비동기 호출하여 데몬 준비 후 HTTP 200 OK 및 재순위화 결과를 정상 반환합니다.
2. **Given** Reranker 모델 가중치가 없는 경우, **When** `/v1/rerank` 요청이 도착하면, **Then** 모델 자동 다운로드 및 가동 후 응답을 리턴하며 503 반환을 방지합니다.

---

### Edge Cases

- **설정 파일 부재 시**: `samples/config.json` 및 `.env` 부재 시 `127.0.0.1`로 기본 폴백하고 사용자에게 `samples/config.json` 설정 가이드 안내 출력.
- **Reranker 모델 로딩 초과**: 30초 내 8091 포트 미개방 시 503 응답과 명확한 Retry-After 헤더 리턴.

---

## 3. Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `samples/common.py` 내의 모든 특정 IP 하드코딩이 제거되고, `SERVER_HOST` / `.env` / `config.json` 파싱 우선순위에 따라 서버 주소를 리턴해야 함.
- **DoD-002**: `samples/config.json.example` 파일이 명확한 가이드 주석과 함께 제공되어 사용자가 자기 환경에 맞게 IP를 쉽게 변경할 수 있어야 함.
- **DoD-003**: `POST /v1/rerank` 요청 시 8091 Reranker 백엔드의 온디맨드 readiness 보장을 통해 503 에러가 해결되어야 함.
- **DoD-004**: 통합 테스트 수트(`tests/integration/test_sample_scripts_and_reranker.py`) 통과.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (설정 기반 서버 IP 파싱)**: `samples/common.py`는 `SERVER_HOST` 환경변수 -> `samples/.env` -> `samples/config.json` 순으로 서버 IP를 파싱하고 소스코드 내 특정 IP 하드코딩을 금지해야 한다.
- **FR-002 (Reranker 프록시 온디맨드 가동)**: `src/api/routes/inference_api.py`의 `reverse_proxy`는 `/v1/rerank` 요청 수신 시 `auxiliary_manager.ensure_rerank_resident()`를 호출하여 8091 백엔드 가동 상태를 보장한 후 요청을 전달해야 한다.
- **FR-003 (Embedding 프록시 온디맨드 가동)**: `reverse_proxy`는 `/v1/embeddings` 요청 수신 시 `auxiliary_manager.ensure_embedding_resident()`를 호출하여 8090 백엔드 가동 상태를 보장해야 한다.
- **FR-004 (샘플 설정 예시 파일 표준화)**: `samples/config.json.example`을 제공하여 개발 플랫폼(`10.0.0.x`) 및 서비스 플랫폼(`192.168.0.x`) 환경에 따른 설정 방법 가이드를 명시해야 한다.

---

## 5. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 소스코드 내 특정 IP 하드코딩 건수 0건 달성.
- **SC-002**: `samples/config.json` 설정에 따라 개발 대역(`10.0.0.x`) 및 서비스 대역(`192.168.0.x`)에서 샘플 스크립트 100% 정상 작동.
- **SC-003**: `python samples/sample_04_reranking.py` 실행 시 HTTP 503 에러 0건 및 정상 200 OK 응답 수렴.

---

## 6. Assumptions

- 샘플 스크립트는 `samples/config.json` 또는 `SERVER_HOST` 환경변수를 통해 연결 대상 서버 주소를 전달받습니다.
- 개발 플랫폼 서브넷 대역은 `10.0.0.x`이며, 서비스 플랫폼 서브넷 대역은 `192.168.0.x`입니다.
- BGE Reranker v2 M3 모델은 `bge-reranker-v2-m3` ID로 `model_catalog.json`에 정의되어 있습니다.

---

## 7. Clarifications

### Session 2026-08-03
- **Q**: 샘플 스크립트 IP 설정 방식 (하드코딩 금지 여부) → **A**: 소스코드 내 IP 하드코딩은 엄격히 금지됨. `samples/common.py`는 `SERVER_HOST` 환경변수 -> `samples/.env` -> `samples/config.json` 순으로 설정을 로드하며, 미설정 시 기본 `127.0.0.1`로 안전하게 폴백함. 사용자는 `samples/config.json` 또는 환경변수를 통해 개발 플랫폼(`10.0.0.x`) 또는 서비스 플랫폼(`192.168.0.x`)의 서버 IP를 자유롭게 설정할 수 있음.
