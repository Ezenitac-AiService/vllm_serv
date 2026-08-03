# Sample Suite Interface Contract: 12개 실습 예제 스크립트 규격

**Feature Branch**: `088-openai-sdk-samples`  
**Date**: 2026-08-03

---

## 1. 1:1 대칭 실습 예제 매핑 규격 (12 Files Specification)

모든 실습 예제 스크립트는 `uv run python samples/[filename]` 형태로 단독 실행 가능해야 하며, `httpx` 버전과 `openai` SDK 버전이 동일한 기능, 동일한 입력 데이터, 동일한 터미널 출력 형식을 유지합니다.

| 스크립트 번호 | httpx REST API 스크립트 | OpenAI SDK 스크립트 | 주요 실습 내용 및 엔드포인트 |
|:---:|---|---|---|
| **01** | `sample_01_chat.py` | `openai_01_chat.py` | 일반 대화 (`/v1/chat/completions`) & `<think>` 태그 정제 |
| **02** | `sample_02_model_params.py` | `openai_02_model_params.py` | 모델 제어 (`temperature=0.0`, `stop=["\n"]`) |
| **03** | `sample_03_embedding.py` | `openai_03_embedding.py` | BGE M3 단일/배치 수치 벡터 추출 (`/v1/embeddings`) |
| **04** | `sample_04_reranking.py` | `openai_04_reranking.py` | BGE Reranker v2 M3 문서 관련도 재순위화 (`/v1/rerank`) |
| **05** | `sample_05_structured_output.py` | `openai_05_structured_output.py` | 단일 비정형 문장 Pydantic 객체 파싱 |
| **06** | `sample_06_structured_output_batch.py` | `openai_06_structured_output_batch.py` | 다중 비정형 문장 배치 Pydantic 객체 일괄 파싱 |

---

## 2. CLI 실행 인터페이스 및 환경 변수 규격

### 실행 표준 명령
```bash
uv run python samples/sample_01_chat.py
uv run python samples/openai_01_chat.py
```

### 동적 환경 변수 오버라이드 (Environment Overrides)
- `SERVER_HOST`: 서빙 서버 IP 주소 지정 (`SERVER_HOST=http://192.168.0.80 uv run python samples/openai_01_chat.py`)
- `OPENAI_API_KEY`: API Key 지정 (기본값: `"EMPTY"`)
- `REAL_API_CALL`: 1 활성화 시 실제 네트워크 통신 실측 검증 수행

---

## 3. 터미널 출력 및 반환 코드 규격

- **성공 반환 코드**: `exit code 0` 및 반환값 `True`
- **실패 반환 코드**: `exit code 1` 및 반환값 `False` (예외 메시지 친절 출력)
- **서버 상태 점검 공통 출력**:
  ```text
  =================================================================
  📌 01. 비전공자용 OpenAI 규격 일반 대화 API 호출 예제
  =================================================================
  📡 [요청 전송] http://192.168.0.80:8081/v1/chat/completions (모델: qwen3.5-4b)

  ✅ [응답 성공]
  -----------------------------------------------------------------
  💬 AI 답변: vllm_serv는 Qwen3.5 및 Gemma4 모델을 고성능으로 서빙하는 플랫폼입니다.
  -----------------------------------------------------------------
  📊 정지 사유: stop
  📊 토큰 사용량: 프롬프트 25토큰 | 생성 18토큰 | 총 43토큰
  ```

---

## 4. `uv sync` 가상환경 복원 계약

- **`pyproject.toml` 필수 패키지 명세**:
  ```toml
  [project]
  name = "vllm_serv"
  version = "0.1.0"
  dependencies = [
      "openai>=1.0.0",
      "httpx>=0.27.0",
      "pydantic>=2.0.0",
      "pytest>=8.0.0"
  ]
  ```
- **복원 커맨드**: `uv sync`
- **규약**: `.venv` 폴더가 없는 상태에서 `uv sync` 단 한 번의 실행으로 가상환경을 100% 자동 구축하고, `uv run python samples/...` 실행을 가능하게 함.
