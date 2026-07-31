# Research: vllm_serv API 예제 샘플 스크립트 작성 (sample_01 ~ sample_05)

**Feature**: `063-sample-server-api-examples`

## Technical Decisions & Rationale

### Decision 1: 샘플 스크립트 배치 구조 및 파일명 명명 규칙
- **선택된 방식**: 프로젝트 루트에 `samples/` 디렉터리를 신설하고 `sample_01_chat.py`, `sample_02_model_params.py`, `sample_03_embedding.py`, `sample_04_reranking.py`, `sample_05_structured_output.py` 명명 규칙 준수
- **이유**: 사용자가 요청한 `sample_숫자.py` 형식을 직관적으로 가시화하고 시나리오별 독립 단일 파일로 실행(`uv run python samples/sample_XX.py`)할 수 있도록 구성함.
- **대안 검토**: `examples/` 또는 `scripts/samples/` 배치 — 사용자 지시서의 `sample_숫자.py` 직관성과 가상환경 표준 실행 가이드 관점에서 루트 `samples/` 배치가 최적임.

### Decision 2: HTTP 클라이언트 라이브러리 선정 (`httpx`)
- **선택된 방식**: `httpx` 동기/비동기 HTTP 클라이언트 사용
- **이유**: `httpx`는 프로젝트 의존성(`pyproject.toml`)에 이미 등록되어 있으며, OpenAI 호환 REST API 호출(`/v1/chat/completions`, `/v1/embeddings`)을 가볍고 직관적으로 지원함.
- **대안 검토**: `requests` (추가 라이브러리 설치 필요), `openai` 파이썬 SDK (C++ native 서빙 포트별 다중 인스턴스 직접 호출 시 HTTP REST 인드포인트 직관성이 우수함).

### Decision 3: 레거시 정밀 추출 Pydantic 스키마 연동 메커니즘
- **선택된 방식**: `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py` 모듈 직접 임포트 및 Pydantic `model_validate_json()` / `model_json_schema()` 활용
- **이유**: 레거시 도메인 스키마에 정의된 주식 분석 (`StockAnalysisItem`) 및 리뷰 감성 분석 (`ReviewSentimentItem`) 클래스를 그대로 재활용하여 LLM 시스템 프롬프트에 JSON Schema 지시어를 주입하고, 모델 생성 결과 응답 텍스트를 Pydantic 객체로 실체적 파싱 검증함.

### Decision 4: 예외 처리 및 사용자 친화적 에러 가이드
- **선택된 방식**: 포트별(8081, 8090, 8091) 연결 실패(`ConnectError`) 발생 시 `[ERROR]` 로그와 함께 `./start_server.sh` 구동 명령 및 사용법 한국어 안내 출력
- **이유**: 개발 서버가 구동 중이지 않은 상태에서 샘플 스크립트 실행 시 파이썬 트레이스백 스택으로 붕괴되지 않고 명확한 조치법을 제시함.
