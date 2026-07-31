# Research Document: 레거시 추출 스크립트 자체 서버 LLM 연동 전환 (036-legacy-extraction-llm)

## Technical Decisions & Rationale

### 1. 로컬 LLM 엔드포인트 바인딩 주소 및 환경 변수 계층 구조

- **Decision**: `OpenAI(base_url=..., api_key=...)` 클라이언트 초기화 시 엔드포인트 URL을 `OPENAI_BASE_URL` -> `VLLM_API_BASE` -> `http://10.0.0.41:8000/v1` (기본값)의 순서로 탐색하도록 구현합니다. `localhost`나 `120.0.0.1`은 주소로 사용하지 않습니다.
- **Rationale**: 사용자의 명시적 요청에 따라 개발 플랫폼 호스트 IP(`10.0.0.41`)를 기본 연결 주소로 삼고, 환경 변수를 통해 타 네트워크 대역(예: `192.168.0.x`)에서도 유연하게 오버라이드할 수 있도록 보장합니다.
- **Alternatives Considered**: `localhost` 고정 (사용자 지침으로 거부됨), `127.0.0.1` (서브넷 격리 환경 미지원으로 거부됨).

### 2. Groq API 키 제거 및 로컬 vLLM 인증 처리

- **Decision**: `api_key=os.getenv("OPENAI_API_KEY", "EMPTY")` 구성을 사용하여 `GROQ_API_KEY` 의존성 및 외부 Groq 서버 호출(`https://api.groq.com/openai/v1`)을 완전히 제거합니다.
- **Rationale**: vLLM OpenAI 호환 엔드포인트는 API 키로 임의의 문자열(`"EMPTY"`)을 수용하므로, 외부 키 발급이나 통신 없이 100% 오프라인/로컬 독립 실행이 가능합니다.
- **Alternatives Considered**: Groq API 키 유지 (외부 의존성 발생으로 거부됨).

### 3. 다중 모델 서빙 라인업 지원 및 순환(Rotation) 검증

- **Decision**: `gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 모델명을 `MODEL_NAME` / `OPENAI_MODEL_NAME` 환경 변수로 동적 수용하며, 테스트 파이프라인에서 해당 모델 목록에 대해 순차적으로 호출 검증이 가능하도록 설계합니다.

- **Rationale**: 명세 FR-007에 따라 다양한 소형/대형 모델 규격에서의 추출 및 정제문(`refined_sentence`) 생성 무결성을 손쉽게 검증할 수 있습니다.
- **Alternatives Considered**: 단일 모델명 하드코딩 (다중 모델 테스트 불가능으로 거부됨).

### 4. 서버 연결 실패 및 예외 처리 가드레일

- **Decision**: LLM 호출 시 `openai.APIConnectionError`, `openai.APITimeoutError` 발생 시 예외를 포착하여 `[시스템] 로컬 LLM 서버 연결 실패: http://10.0.0.41:8000/v1 서버 상태를 확인하세요` 메시지를 출력하고 빈 결과(`[]`)를 안전하게 반환합니다.
- **Rationale**: LLM 서버 미구동 상태에서도 스크립트 비정상 종료 없이 후속 처리 및 로그 표출이 안정적으로 이루어집니다.
- **Alternatives Considered**: 예외 무시 또는 Unhandled Exception 방치 (시스템 크래시 유발로 거부됨).
