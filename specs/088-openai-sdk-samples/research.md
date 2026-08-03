# Research & Technical Decisions: OpenAI API 실습 예제 수트 및 uv 복원 환경

**Feature Branch**: `088-openai-sdk-samples`  
**Date**: 2026-08-03

---

## 1. OpenAI 파이썬 SDK 클라이언트 초기화 및 인증 수신 방식

### Decision: `from openai import OpenAI` 및 `api_key="EMPTY"` 기본 적용

- **선택 내용**: `client = OpenAI(base_url=f"{server_host}:{main_port}/v1", api_key=os.environ.get("OPENAI_API_KEY", "EMPTY"))`
- **선택 사유**:
  - OpenAI 파이썬 SDK v1.0+ 규격은 `api_key`가 설정되지 않으면 `OpenAIError` 예외를 발생시킵니다.
  - vllm_serv 백엔드는 로컬/플랫폼 인퍼런스 서버로서 API Key 검증을 요구하지 않거나 더미 키를 허용하므로 기본값으로 `"EMPTY"`를 지정하여 클라이언트 초기화 오류를 철저히 방지합니다.
- **기타 검토된 대안**:
  - `httpx` 커스텀 헤더 직접 주입: 저수준 HTTP 통신 코드가 노출되므로 OpenAI SDK 사용 목적에 부합하지 않아 기각.

---

## 2. 서버 IP (`192.168.0.80` 등), 포트, 모델명 하드코딩 완전 배제 및 동적 로드 방식

### Decision: `samples/config.json` 및 `common.py` 연동 동적 파싱

- **선택 내용**:
  - `samples/config.json`에 `server_host`, `main_port`, `embedding_port`, `rerank_port`, `model_name`을 정의.
  - `common.py` 내 `get_config()` 및 `get_server_host()` 유틸리티 함수를 통해 `config.json` ➡️ `.env` ➡️ 환경변수(`SERVER_HOST`) ➡️ 자동 IP 감지 순으로 안전하게 폴백(Fallback) 동적 바인딩.
- **선택 사유**:
  - 서비스 플랫폼 IP(`192.168.0.80`)나 원격 훈련 서버 IP가 변경되어도 코드 수정 없이 `config.json` 수정만으로 실습 환경 100% 대응 가능.
- **기타 검토된 대안**:
  - 각 파이썬 스크립트 상단에 `SERVER_HOST = "192.168.0.80"` 변수 지정: 플랫폼 IP 이동 시 12개 파일 전수를 수정해야 하므로 기각.

---

## 3. OpenAI SDK 환경에서의 Reranker (/v1/rerank) 호출 처리 방식

### Decision: `client.post` 커스텀 엔드포인트 요청 또는 SDK 호환 인터페이스 사용

- **선택 내용**:
  - `openai` 공식 SDK 클라이언트 객체의 `client.post("/rerank", body=payload)` (또는 `client.with_raw_response` / REST wrapper)를 사용하여 `OpenAI` 클라이언트 세션 내에서 통신 수행.
- **선택 사유**:
  - official OpenAI REST spec에는 `/v1/rerank`가 표준으로 존재하지 않으나 vllm_serv 백엔드가 확장 포트로 제공하므로, SDK 클라이언트의 세션 풀 및 기본 통신 객체를 활용하여 코드 통일성 유지.
- **기타 검토된 대안**:
  - Reranker 전용 별도 외부 라이브러리 도입: 훈련생의 의존성 부담을 가중시키므로 기각.

---

## 4. 단일 및 배치(Batch) Pydantic 구조화 응답 파싱 방식

### Decision: Pydantic v2 `BaseModel` + `response_format={"type": "json_object"}`

- **선택 내용**:
  - `openai_05_structured_output.py`: 1개 비정형 텍스트 ➡️ `StockAnalysisResponse` 파싱.
  - `openai_06_structured_output_batch.py`: N개 비정형 텍스트 묶음 ➡️ `StockAnalysisResponse(results=List[StockCommentItem])` 리스트 파싱.
- **선택 사유**:
  - LLM에게 JSON Schema를 프롬프트에 주석으로 제공하고, `response_format={"type": "json_object"}`를 전달하여 엄격한 JSON 배열 응답 유도 후 Pydantic `model_validate_json()`으로 타입 안전성 100% 검증.
- **기타 검토된 대안**:
  - 정규표현식(Regex) 기반 텍스트 추출: JSON 구조 파손 시 신뢰성이 떨어지므로 기각.

---

## 5. `.venv` 배제 및 `uv sync` 가상환경 100% 복원 패키지 체계

### Decision: 루트/samples 연동 `pyproject.toml` 및 `uv.lock` 명세 제공

- **선택 내용**:
  - `.venv` 디렉토리는 배포 팩 및 Git에 포함시키지 않음 (`.gitignore` 및 배포 스크립트에 배제).
  - 훈련생이 `samples/` 폴더를 전달받아 `uv sync` 명령을 실행할 때 `pyproject.toml`과 `uv.lock`을 통해 `openai`, `httpx`, `pydantic`, `pytest` 패키지가 10초 이내에 동일한 버전으로 정확히 자동 설치되도록 구성.
- **선택 사유**:
  - OS 및 파이썬 마이너 버전 차이로 인한 `.venv` 가상환경 오염 방지 및 헌법 VI조(uv 표준 환경 관리) 완벽 준수.
