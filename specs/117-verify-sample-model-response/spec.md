# Feature Specification: sample 예제 스크립트 호출 모델 대 응답 모델 일치성 검증 및 하드코딩 제거 (Verify Sample Scripts Model Parity & Remove Hardcoded Values)

**Feature Name**: `verify-sample-model-response`  
**Feature Directory**: `specs/117-verify-sample-model-response`  
**Created**: 2026-08-08  
**Status**: Draft  

**Input**: User description: "벤치마크와 테스트에서는 실제로 모델을 바꿔가며 서비스하는게 확인되었는데, /home/dev/storage/vllm_serv/sample 폴더의 실습파일들은 호출하는 모델이 실제로 응답하는 모델이 맞는지 검증하는 스펙을 작성. 그리고, sample 폴더의 파일들에 하드코딩된 값들이 너무 많은것 같아. config.json 이외에는 하드코딩, 목업은 없어야 해"

---

## Clarifications

### Session 2026-08-08

- Q: `sample/config.json` 및 서버 IP 토폴로지 설정 지정 방식 → A: 실습 배포 환경은 `192.168.0.175` (`192.168.0.x` 대역)를 기본 호스트로 유지하되, 현재 개발 플랫폼 환경 IP (`10.0.0.41`) 및 로컬 (`127.0.0.1`)을 `sample/common.py` 자동 호스트 탐색 목록에 포함하고 `config.json` 및 환경변수(`SERVER_HOST`)를 통해 유연하게 호스트 전환이 가능하도록 동적 감지 레이어를 연동함.
- Q: `sample/` 폴더 내 소스 파일의 하드코딩 및 목업 제거 범위 → A: `sample/` 폴더의 모든 실습 및 공통 스크립트(`sample/common.py`, `sample_*.py`, `openai_*.py` 등) 내 소스 코드 상에 하드코딩된 IP 주소, 포트 번호, 가용 모델 리스트, 타임아웃, 더미 텍스트/목업을 전면 제거하고, 오직 `sample/config.json` (및 환경변수 `SERVER_HOST`/`OPENAI_BASE_URL`)을 단일 진실 출처(Single Source of Truth)로 동적 로드하도록 정제함.

---

## User Value & Business Need

학습자 및 서비스 개발자가 `/home/dev/storage/vllm_serv/sample` 폴더의 교육용 실습 스크립트를 구동할 때, 자신이 호출 요청한 LLM 모델 ID(예: `qwen3.5-4b`, `gemma4-e4b` 등)와 서버가 실제 핫스왑 후 생성하여 반환한 응답 객체의 `model` 필드가 100% 일치함을 직관적이고 명시적으로 검증할 수 있도록 보장합니다. 또한 소스 코드 내 불필요한 하드코딩 값과 더미 목업을 제거하고 `sample/config.json`을 단일 진실 출처로 다듬어 개발 플랫폼(`10.0.0.41`) 및 배포 환경(`192.168.0.175`) 간의 설정 유지보수성을 극대화합니다.

---

## User Scenarios & Testing *(mandatory)*

### Story 1: sample 실습 스크립트 실행 시 호출 모델 대 응답 모델 일치 검증 및 시각화 (Priority: P1) 🎯 MVP

**User Role**: 교육 참가자 및 API 서비스 이용자  

**As a** vllm_serv 실습 스크립트 실행자  
**I want** `sample/sample_04_model_switch.py` 및 `sample/openai_04_model_switch.py` 등 실습 코드를 실행했을 때, 요청한 `model` ID와 서버 응답 페이로드 내 `model` 필드가 일치하는지 자동으로 검증되고 콘솔 리포트에 명확히 표시되기를 원한다.  
**So that** 백엔드 모델 핫스왑이 실제 요청 모델로 완료되었음을 실측으로 확신할 수 있다.

**Why this priority**: 실습생이 모델 스위칭 결과를 직접 눈으로 검증할 수 있는 핵심 신뢰성 지표임.

**Independent Test**: `uv run python sample/sample_04_model_switch.py` 실행 시 콘솔에 `[모델 일치 검증]: 요청(qwen3.5-4b) == 응답(qwen3.5-4b) ✅` 형태의 검증 로그 및 성능 요약이 출력됨.

**Acceptance Scenarios**:

1. **Scenario 1.1: httpx 샘플 응답 모델 일치 검증**:
   - **Given**: API 서버가 정상 구동 중인 상태 (개발 IP `10.0.0.41` 또는 배포 IP `192.168.0.175` / `127.0.0.1`)
   - **When**: `sample/sample_04_model_switch.py`에서 `qwen3.5-2b` 모델 요청 전송
   - **Then**: 응답 JSON의 `res["model"]`이 `qwen3.5-2b`와 일치하는지 확인하고, 콘솔에 검증 성공(`✅`)을 출력한다.

2. **Scenario 1.2: OpenAI SDK 샘플 응답 모델 일치 검증**:
   - **Given**: API 서버가 정상 구동 중인 상태
   - **When**: `sample/openai_04_model_switch.py`에서 `gemma4-e4b` 모델 요청 전송
   - **Then**: SDK 응답 객체의 `completion.model`이 `gemma4-e4b`와 일치하는지 확인하고, 콘솔에 검증 성공(`✅`)을 출력한다.

---

### Story 2: sample/ 폴더 코드 내 하드코딩 및 더미 목업 전면 제거 (Priority: P1) 🎯 MVP

**User Role**: 코드 유지보수자 및 교육 진행자  

**As a** 실습 코드 관리자  
**I want** `sample/` 폴더 내 모든 파이썬 파일에서 하드코딩된 IP, 포트, 모델 리스트, 목업 텍스트를 제거하고 `sample/config.json`에서 유연하게 로드하도록 정제되기를 원한다.  
**So that** 서버 IP나 포트, 벤치마크 설정이 변경되어도 파이썬 소스 코드를 수정하지 않고 `config.json` 수정만으로 완벽히 반영된다.

**Why this priority**: 하드코딩 매직 넘버/IP로 인한 환경 이식성 저하 및 오작동 위험 방지.

**Independent Test**: `sample/` 하위 `.py` 파일 전수 스캔 시 하드코딩된 IP/모델 리스트/목업 텍스트가 0건이고 `load_sample_config()`를 통해 완전 동적 구성됨을 확인.

**Acceptance Scenarios**:

1. **Scenario 2.1: config.json 단일 진실 출처 로드**:
   - **Given**: `sample/config.json`에 `server_host`, `main_port`, `model_benchmarks`가 설정된 상태
   - **When**: `sample/common.py` 및 예제 스크립트 실행
   - **Then**: 코드 내 하드코딩 없이 `config.json`에서 호스트/포트/모델 카탈로그/타임아웃 설정을 100% 동적 로드한다.

---

### Story 3: API Gateway 응답 객체 모델 필드 정합성 보장 (Priority: P1) 🎯 MVP

**User Role**: API 백엔드 개발자  

**As a** API Gateway 엔지니어  
**I want** `POST /v1/chat/completions` 엔드포인트가 모델 핫스왑 후 백엔드 추론 결과 응답을 반환할 때, 응답 페이로드의 `model` 필드가 실제 핫스왑 로드된 모델 ID로 정확히 전달되기를 원한다.  
**So that** MOCK 서버 모드 및 프록시 스트리밍 응답 시에도 클라이언트가 수신하는 JSON의 `model` 값이 요청 모델과 정확히 일치한다.

**Why this priority**: API 표준 규격 준수 및 클라이언트 응답 파싱 정합성의 기본 전제조건임.

**Independent Test**: MOCK 및 실물 백엔드 서빙 응답 모두에서 `response.json()["model"]`이 요청 모델 ID와 일치함을 단위 테스트로 검증.

**Acceptance Scenarios**:

1. **Scenario 3.1: MOCK 백엔드 응답 모델 동적 반영**:
   - **Given**: `MOCK_LLAMA_SERVER=1` 환경변수가 설정된 상태
   - **When**: `POST /v1/chat/completions`로 `model: "gemma4-e2b"` 전송
   - **Then**: MOCK 응답 JSON의 `model` 필드가 `"gemma4-e2b"`로 동적 설정되어 반환된다.

---

### Story 4: 샘플 스크립트 응답 모델 일치 자동화 단위 테스트 (Priority: P2)

**User Role**: QA 및 CI/CD 엔지니어  

**As a** 품질 검증 담당자  
**I want** `tests/unit/test_sample_model_switch.py`에 호출 모델 대 응답 모델 교차 검증 테스트를 포함하기를 원한다.  
**So that** 코드 변경 후에도 샘플 스크립트의 응답 검증 로직이 깨지지 않음을 자동화된 회귀 테스트로 보장할 수 있다.

**Why this priority**: 지속적 통합(CI) 시 샘플 코드의 정상 동작 여부를 감시함.

**Independent Test**: `uv run pytest tests/unit/test_sample_model_switch.py` 100% 통과.

---

### Edge Cases

- 서버 응답에 `model` 필드가 누락되거나 다른 모델 이름이 들어올 경우: 샘플 스크립트가 이를 즉시 감지하여 `❌ [모델 불일치 경고]` 로그를 출력하고 예외를 발생시켜야 함.
- 핫스왑 실패 후 fallback 응답 반환 시: 검증 단계에서 요청 모델과 다름을 감지하고 실패 원인을 명시해야 함.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `sample/` 폴더 내 실습 파일(`sample_04_model_switch.py`, `openai_04_model_switch.py`) 실행 시 요청 모델 ID와 응답 페이로드 내 `model` 필드의 일치 여부를 실시간 검증하고 콘솔에 출력.
- **DoD-002**: `src/api/routes/inference_api.py` MOCK 및 프록시 응답 처리 시 요청 `model` ID가 응답 객체에 정확히 유지되는지 확인.
- **DoD-003**: `sample/common.py` 감지기에 개발 플랫폼 IP(`10.0.0.41`) 및 배포 IP(`192.168.0.175`) 호스트 동적 전환 레이어 구성.
- **DoD-004**: `sample/` 폴더 내 파이썬 코드상 하드코딩된 주소/포트/모델/목업 텍스트를 전면 제거하고 `sample/config.json` 기반 단일 진실 출처 동적 로드 구조로 완료.
- **DoD-005**: `uv run pytest tests/unit/test_sample_model_switch.py` 실행 시 모델 일치성 검증 테스트 100% 통과.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `sample/sample_04_model_switch.py` (httpx) 및 `sample/openai_04_model_switch.py` (OpenAI SDK) 스크립트는 API 응답 객체에서 `model` 필드를 추출하여 요청 전송한 `model` ID와의 일치 여부를 비교 검증해야 한다.
- **FR-002**: 샘플 스크립트의 성능 요약 출력(`print_performance_summary` 또는 콘솔 출력) 시, 요청 모델명과 응답 모델명이 일치함을 시각적 태그(`[모델 검증: 요청(X) == 응답(X) ✅]`)로 표시해야 한다.
- **FR-003**: `src/api/routes/inference_api.py` 역방향 프록시 핸들러는 MOCK 서버 응답 생성 시 요청 페이로드의 `model` ID를 응답 JSON의 `model` 필드에 동적으로 대입해야 한다.
- **FR-004**: 요청 모델과 응답 모델이 불일치하는 상황 발생 시, 샘플 스크립트는 이를 감지하여 불일치 경고(`❌ [모델 불일치 오류]`)를 발생시키고 해당 요청 건을 실패로 기록해야 한다.
- **FR-005**: `tests/unit/test_sample_model_switch.py`에 호출 모델과 응답 모델의 일치성 검증 기능을 단정(assert)하는 단위 테스트 케이스를 수록해야 한다.
- **FR-006**: `sample/common.py`의 `get_server_host()` 감지기 및 `sample/config.json` 호스트 설정은 배포 타겟 IP(`192.168.0.175`)와 개발 플랫폼 IP(`10.0.0.41`) 및 로컬(`127.0.0.1`)을 동적으로 감지/전환 지원해야 한다.
- **FR-007**: `sample/` 폴더 내 파이썬 파일에는 `sample/config.json` 이외의 코드 자체에 하드코딩된 IP 주소, 포트 번호, 모델 리스트, 타임아웃, 목업 텍스트가 포함되어서는 안 되며, 모든 설정값은 `config.json`으로부터 로드해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run python sample/sample_04_model_switch.py` 및 `uv run python sample/openai_04_model_switch.py` 구동 시 전수 모델 요청에 대해 100% 응답 모델 일치 검증 통과 (`✅`).
- **SC-002**: `sample/` 폴더 소스 파이썬 파일 전수 검사 시 하드코딩 매직 넘버/IP/목업 텍스트 0건.
- **SC-003**: `uv run pytest tests/unit/test_sample_model_switch.py` 및 관련 테스트 수트 100% PASS.
- **SC-004**: 불일치 모델 페이로드 주입 시 100% 감지 및 에러 보고.

---

## Assumptions

- 샘플 스크립트는 `sample/common.py`에 정의된 공통 헬퍼 함수를 통해 응답 모델 검증 결과를 공유하거나 직접 검증할 수 있음.
- MOCK 서버 환경에서도 실제 서빙 환경과 동일한 OpenAI 규격 응답 구조(`model`, `choices`, `usage`)를 유지함.
- 실습 배포 타겟 IP는 `192.168.0.175` (`192.168.0.x` 대역)이며, 현재 개발 플랫폼 IP(`10.0.0.41`) 및 로컬(`127.0.0.1`) 주소를 `sample/common.py` 감지 파이프라인에서 자동 헬스체크 지원함.
- `sample/config.json`이 `sample/` 폴더 내 모든 스크립트 설정의 단일 진실 출처(Single Source of Truth)가 됨.
