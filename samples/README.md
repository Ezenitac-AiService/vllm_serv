# 🎓 vllm_serv AI 서비스 개발자 양성과정 교육용 예제 실습 가이드

본 폴더(`samples/`)는 **AI 서비스 개발자 양성과정 비전공자 훈련생**을 위해 준비된 **OpenAI API 표준 규격 실습 코드 수트**입니다.

복잡한 파이덴틱(Pydantic) 모델이나 난해한 라이브러리 추상화 없이, 글로벌 AI 산업 표준인 **OpenAI 공식 API 규격**과 파이썬 기본 딕셔너리(`dict`) 구조만으로 5분 만에 실습을 완성할 수 있습니다.

---

## 🚀 5분 완성 실습 순서

모든 명령어는 가상환경 격리 표준인 `uv run` 환경에서 수행합니다.

### 1단계: 일반 대화(Chat Completions) 호출 실습
```bash
uv run python samples/sample_01_chat.py
```
- **배우는 내용**: OpenAI 호환 대화 API 규격(`messages`, `temperature`, `max_tokens`)을 파이썬 딕셔너리로 다루고 AI 모델 답변 수신하기

### 2단계: 모델 제어 파라미터(Temperature & Stop) 실습
```bash
uv run python samples/sample_02_model_params.py
```
- **배우는 내용**: `temperature` 조절을 통한 답변 정확성 보장 및 `stop` 옵션을 통한 특정 문자 조기 생성을 중단 제어하기

### 3단계: BGE M3 1024차원 임베딩(Embedding) 벡터 추출 실습
```bash
uv run python samples/sample_03_embedding.py
```
- **배우는 내용**: 텍스트를 AI 컴퓨터가 이해하는 1024차원 수치 벡터(Vector)로 변환하는 RAG 필수 개념 익히기

### 4단계: BGE Reranker v2 M3 문서 관련도 재순위화 실습
```bash
uv run python samples/sample_04_reranking.py
```
- **배우는 내용**: 사용자 질문과 후보 문서 간의 의미적 유사도 점수(Relevance Score)를 측정하고 재정렬하기

---

## 💡 훈련생 팁 (Troubleshooting)

- **서버 연결 실패 에러가 나올 때**:
  ```bash
  ./status_server.sh  # 서버 구동 상태 확인
  ./start_server.sh   # 백그라운드 서버 가동
  ```
- **원격 IP 서버 연결 시**:
  ```bash
  SERVER_HOST=http://192.168.0.xxx uv run python samples/sample_01_chat.py
  ```
