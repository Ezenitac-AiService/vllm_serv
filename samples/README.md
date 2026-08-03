# 🎓 vllm_serv AI 서비스 개발자 양성과정 교육용 예제 실습 가이드

본 폴더(`samples/`)는 **AI 서비스 개발자 양성과정 비전공자 훈련생**을 위해 준비된 **httpx REST API & OpenAI 파이썬 공식 SDK 1:1 대칭 실습 코드 수트 (총 12종)**입니다.

복잡한 객체지향 추상화 클래스 없이, 글로벌 AI 산업 표준인 **OpenAI 공식 파이썬 라이브러리(`from openai import OpenAI`)** 및 **httpx** 요청을 1:1 비교하며 직관적으로 학습할 수 있습니다.

---

## 📦 가상환경 원클릭 복원 (`uv sync`)

본 실습 팩에는 용량 오염을 방지하기 위해 `.venv` 디렉토리가 포함되어 있지 않습니다.  
실습을 시작하기 전, 다음 명령어 **단 한 번으로** 의존성 패키지를 100% 즉시 원복하세요:

```bash
# 1. 가상환경 의존성 자동 동기화 및 원복
uv sync

# 2. 패키지 원복 정상 작동 확인
uv run python -c "import openai, httpx, pydantic; print('✅ uv 가상환경 복원 성공!')"
```

---

## ⚙️ 동적 설정 관리 (`samples/config.json`)

서버 IP 주소(서비스 플랫폼 `192.168.0.80` 등), 포트번호, 모델명은 하드코딩되지 않고 `samples/config.json`에서 동적으로 로드됩니다.

```json
{
  "server_host": "http://192.168.0.80",
  "main_port": 8081,
  "embedding_port": 8090,
  "rerank_port": 8091,
  "default_model": "qwen3.5-4b"
}
```

- **원격/플랫폼 IP 일시 오버라이드 실행 예시**:
  ```bash
  SERVER_HOST=http://192.168.0.80 uv run python samples/openai_01_chat.py
  ```

---

## 🚀 1:1 대칭 실습 예제 수트 (총 12종)

모든 실습 스크립트는 가상환경 격리 표준인 `uv run python ...`으로 실행합니다.

### 1단계: 일반 대화 (Chat Completions) 1:1 비교
```bash
# httpx REST API 버전
uv run python samples/sample_01_chat.py

# OpenAI 공식 SDK 버전
uv run python samples/openai_01_chat.py
```
- **배우는 내용**: `messages`, `temperature`, `max_tokens` 규격 및 `<think>` 태그 정제 1:1 비교

### 2단계: 모델 제어 파라미터 (Temperature & Stop) 1:1 비교
```bash
# httpx REST API 버전
uv run python samples/sample_02_model_params.py

# OpenAI 공식 SDK 버전
uv run python samples/openai_02_model_params.py
```
- **배우는 내용**: `temperature=0.0` 지식 답변 유도 및 `stop=["\n"]` 생성 중단 제어 1:1 비교

### 3단계: 단일 및 배치(Batch) 텍스트 임베딩 수치 벡터 추출 1:1 비교
```bash
# httpx REST API 버전
uv run python samples/sample_03_embedding.py

# OpenAI 공식 SDK 버전
uv run python samples/openai_03_embedding.py
```
- **배우는 내용**: 단일 텍스트 및 다중 문장 리스트(`input=[...]`) 묶음을 1024차원 수치 벡터로 변환하는 배치 처리 1:1 비교

### 4단계: BGE Reranker v2 M3 문서 관련도 재순위화 1:1 비교
```bash
# httpx REST API 버전
uv run python samples/sample_04_reranking.py

# OpenAI 공식 SDK 버전
uv run python samples/openai_04_reranking.py
```
- **배우는 내용**: 질문(Query)과 후보 문서(Documents) 간 의미적 유사도 점수(Relevance Score) 측정 1:1 비교

### 5단계: 단일 Pydantic 구조화된 출력 (Structured Output) 1:1 비교
```bash
# httpx REST API 버전
uv run python samples/sample_05_structured_output.py

# OpenAI 공식 SDK 버전
uv run python samples/openai_05_structured_output.py
```
- **배우는 내용**: `response_format={"type": "json_object"}` 및 Pydantic 단일 모델 타입 검증 1:1 비교

### 6단계: [신설] 배치(Batch) Pydantic 구조화된 출력 1:1 비교
```bash
# httpx REST API 버전
uv run python samples/sample_06_structured_output_batch.py

# OpenAI 공식 SDK 버전
uv run python samples/openai_06_structured_output_batch.py
```
- **배우는 내용**: 다수의 비정형 댓글 묶음을 1회 요청으로 전달받아 Pydantic `results` 배열 객체 목록으로 일괄 검증 1:1 비교

---

## 💡 훈련생 팁 (Troubleshooting)

- **서버 연결 실패 에러가 나올 때**:
  ```bash
  ./status_server.sh  # 서버 구동 상태 확인
  ./start_server.sh   # 백그라운드 서버 가동
  ```
- **접속 IP 변경이 필요할 때**:
  - `samples/config.json` 파일 내 `"server_host": "http://192.168.0.80"` 수정
