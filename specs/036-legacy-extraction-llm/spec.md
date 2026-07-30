# Feature Specification: 레거시 추출 스크립트 자체 서버 LLM 연동 전환 (Legacy Extraction Scripts Local LLM Integration)

**Feature Branch**: `036-legacy-extraction-llm`

**Created**: 2026-07-30

**Status**: Draft

## Clarifications

### Session 2026-07-30

- Q: 로컬 LLM 서빙 대상 모델 범위 및 테스트 구동 지정 방법 → A: `gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 모델 목록을 순차적으로 순환(Rotate)하거나 환경 변수로 지정하여 각 모델별 추론 결과를 검증할 수 있도록 지원함.

- Q: LLM 엔드포인트 호출 주소 (localhost/120.0.0.1 사용 금지 및 서버 할당 IP 지정) → A: `localhost`나 `120.0.0.1` 루프백 주소를 사용하지 않고, 개발 플랫폼 서버에 실제로 할당된 호스트 LAN IP (현재 개발 플랫폼: `10.0.0.41` / `10.0.0.x` 대역, `NetworkDetector` 감지 IP) 기반 엔드포인트 (기본: `http://10.0.0.41:8000/v1`)로 연결 및 구동함.


## User Scenarios & Testing *(mandatory)*

### User Story 1 - ATEAM 주식 댓글 감성 추출 스크립트 로컬 LLM 연동 (Priority: P1)

개발자 및 연구원은 외부 서비스(Groq API)에 대한 의존성이나 API 키 없이, 자체 서버에서 구동 중인 vLLM 서빙 모델을 통해 종목 토론방 댓글 타임라인 및 메타정보 기반 감성 요소를 파싱할 수 있어야 합니다.

**Why this priority**: 외부 API 키 만료/제한 없이 자체 구축된 vLLM 서빙 인프라를 활용하여 실습 및 마이그레이션 파이프라인을 안정적으로 유지하기 위해 가장 시급합니다.

**Independent Test**: `.legacy/ATEAM_ExtractionItem.py` 스크립트를 독립 실행하여 외부 통신 없이 로컬 vLLM 엔드포인트(`http://localhost:8000/v1`)로부터 감성 추출 JSON 결과를 정상 반환하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 자체 서버 vLLM 모델이 구동 중인 상태에서, **When** `ATEAM_ExtractionItem.py` 스크립트를 실행하면, **Then** 외부 Groq API 호출 없이 로컬 LLM으로부터 주식 댓글 분석 결과를 수신하고 5단계 하이브리드 파이프라인(유의어 정규화, BM25 가드레일 등)을 통과한 JSON 결과를 출력합니다.
2. **Given** `OPENAI_BASE_URL` 또는 `VLLM_API_BASE` 환경 변수가 설정된 상태에서, **When** 스크립트가 클라이언트를 초기화하면, **Then** 지정된 로컬 엔드포인트 및 모델명으로 성공적으로 연결됩니다.

---

### User Story 2 - BTEAM 음식점 리뷰 감성 추출 스크립트 로컬 LLM 연동 (Priority: P2)

개발자 및 연구원은 음식점 리뷰 분석 스크립트 또한 외부 Groq API 대신 자체 서버 LLM을 사용하여 문단 단위 감성 요소 파싱 및 맥락적 대상(target) 복원 작업을 처리해야 합니다.

**Why this priority**: ATEAM 스크립트와 함께 `.legacy/` 내 주요 추출 스크립트의 로컬 LLM 마이그레이션을 완성하여 전체 레거시 파이프라인의 자립성을 확보합니다.

**Independent Test**: `.legacy/BTEAM_ExtractionItem.py` 스크립트를 독립 실행하여 로컬 LLM 연결 및 리뷰 분석 문장/정제문 JSON 결과를 정상 반환하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 자체 서버 LLM 엔드포인트가 동작 중인 환경에서, **When** `BTEAM_ExtractionItem.py` 메인 실행부를 동작시키면, **Then** 로컬 LLM을 통해 리뷰 카테고리/대상 복원 결과를 수신하고 4단계 파이프라인(BM25 오매칭 차단 검증 포함)을 정상 수행합니다.

---

### User Story 3 - 환경 변수 구성 및 설정 유연성 확보 (Priority: P3)

운영자 및 개발자는 외부 API 키(`GROQ_API_KEY`) 하드코딩이나 고정 URL에 의존하지 않고, `.env` 또는 시스템 환경 변수를 통해 로컬 LLM 서버 주소와 모델명을 유연하게 변경할 수 있어야 합니다.

**Why this priority**: 다양한 개발/테스트/프로덕션 서버 환경(포트 변경, 모델 변경 등)에 유연하게 대응하기 위해 필요합니다.

**Independent Test**: `.env` 파일의 `VLLM_API_BASE` 및 `MODEL_NAME` 설정을 변경한 후 두 스크립트가 해당 설정값을 참조하여 로컬 LLM에 접속하는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** `.env` 파일에 `OPENAI_BASE_URL` (기본값: `http://localhost:8000/v1`) 및 `MODEL_NAME` (기본값: 서버 활성 모델)이 설정되어 있을 때, **When** 스크립트가 실행되면, **Then** 설정된 로컬 주소와 모델명으로 클라이언트를 생성합니다.
2. **Given** API 키가 제공되지 않거나 임의의 기본값인 경우에도, **When** 로컬 vLLM 서버에 요청을 보내면, **Then** 인증 에러 없이 정상 응답을 수신합니다.

---

### Edge Cases

- 로컬 vLLM 서버가 실행되지 않았거나 응답하지 않는 경우 (ConnectionRefusedError / Timeout): 예외를 안전하게 포착하고 사용자 친화적인 안내 메시지("[시스템] 로컬 LLM 서버 연결 실패: http://localhost:8000/v1 서버 상태를 확인하세요")를 출력하고 빈 결과(`[]`)를 반환해야 합니다.
- 로컬 LLM 응답에 `<think>...</think>` 태그가 포함되어 있거나 파싱 불가능한 텍스트 형태인 경우: 정규표현식 기반 태그 제거 및 JSON 파싱 폴백이 안전하게 동작해야 합니다.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py` 내의 Groq API 클라이언트 및 모델 설정이 자체 서버 vLLM 엔드포인트 연동으로 전환됨
- **DoD-002**: 두 파일 실행 시 외부 인터넷 연결 없이 로컬 vLLM 서버 기반으로 감성 추출 및 BM25 가드레일 파이프라인이 100% 정상 작동함
- **DoD-003**: 로컬 LLM 연동 및 결과 검증을 위한 자동화된 단위/통합 테스트 코드 작성 및 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 스크립트는 외부 Groq API 호출(`https://api.groq.com/openai/v1`) 및 Groq API 키 의존성을 완전히 제거해야 한다.
- **FR-002**: 스크립트는 `localhost`나 `120.0.0.1` 대신 개발 플랫폼 서버에 실제 할당된 LAN IP (현재: `10.0.0.41` / `10.0.0.x` 대역) 기반의 OpenAI 호환 vLLM 엔드포인트(`http://10.0.0.41:8000/v1` 기본값)를 통해 LLM 추론을 수행해야 한다.
- **FR-003**: `.legacy/ATEAM_ExtractionItem.py` 내 `process_stock_comment_sentiment_extraction()` 함수가 로컬 LLM 서버를 호출하여 주식 댓글 감성 요소 및 `refined_sentence`를 정상 파싱해야 한다.
- **FR-004**: `.legacy/BTEAM_ExtractionItem.py` 내 `process_review_sentiment_extraction()` 함수가 로컬 LLM 서버를 호출하여 리뷰 감성 요소 및 `refined_sentence`를 정상 파싱해야 한다.
- **FR-005**: 환경 변수(`OPENAI_BASE_URL` / `VLLM_API_BASE` 기본값: `http://10.0.0.41:8000/v1` 및 `MODEL_NAME` / `CURRENT_MODEL`)를 조율하여 서버 할당 IP URL 및 모델 이름을 유연하게 설정할 수 있어야 한다.

- **FR-006**: 기존 파이프라인(Kiwi 형태소 토큰화, 유의어 정규화, `HybridBM25Matcher` 오매칭 차단 필터) 및 JSON 반환 구조(`{"results": [...]}`)는 기존 인터페이스와 100% 호환을 유지해야 한다.
- **FR-007**: 로컬 LLM 서빙 모델 설정 시 `gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 모델 라인업을 지원하며, 순차적 모델 순환(Rotation) 또는 선택 지정을 통해 각 모델별 추론 및 파싱 결과를 검증할 수 있어야 한다.



### Key Entities

- **LocalLLMClient**: 자체 서버 vLLM 엔드포인트(`http://localhost:8000/v1`)와 통신하는 OpenAI 규격 기반 로컬 클라이언트 구성 객체
- **ExtractionItemResult**: LLM 추론 및 하이브리드 BM25 오매칭 차단 필터를 통과한 후 반환되는 최종 감성 데이터 객체 (`speaker`, `category`, `sentiment`, `target`, `sentence`, `refined_sentence`)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 외부 인터넷망이나 외부 API 키(`GROQ_API_KEY`) 없이 로컬 LLM 서버 환경만으로 100% 독립 실행 가능
- **SC-002**: 두 레거시 스크립트 실행 시 오류 없이 0.5초~3초 이내에 로컬 LLM 응답 수신 및 결과 추출 완수
- **SC-003**: 기존 하이브리드 BM25 오매칭 차단 기능(`validate_target`) 및 JSON 출력 포맷과의 100% 호환성 보장

## Assumptions

- 자체 서버에 OpenAI 호환 vLLM 서빙 포트(예: `http://localhost:8000/v1`)가 구동 중이거나 실행 가능한 환경이 준비되어 있습니다.
- 로컬 LLM은 JSON output 모드(`response_format={"type": "json_object"}`) 또는 표준 텍스트 JSON 출력을 지원합니다.
- `kiwipiepy` 및 `rank_bm25` 등 기존 로컬 자연어 처리 패키지 환경은 그대로 유지됩니다.
