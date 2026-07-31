# Quickstart & End-to-End Validation Guide: vllm_serv API 예제 샘플 스크립트 (sample_01 ~ sample_05)

**Feature**: `063-sample-server-api-examples`
**Created**: 2026-07-31

## 1. 개요 (Overview)

본 가이드는 `samples/` 디렉터리에 작성되는 5종의 예제 파이썬 스크립트(`sample_01_chat.py` ~ `sample_05_structured_output.py`)를 통해 개발 서버의 LLM(8081), BGE M3 임베딩(8090), BGE Reranker v2 M3(8091) 백엔드를 실측 호출하고 결과를 검증하는 절차를 설명합니다.

---

## 2. 사전 조건 (Prerequisites)

1. vllm_serv 개발 서버 및 백그라운드 모델 그룹 구동 중
   ```bash
   ./status_server.sh
   ```
   (상태: `🟢 구동 중 (RUNNING)`, 8081, 8090, 8091 포트 수신 확인)

2. `uv` 환경 준비 완료 (`uv sync`)

---

## 3. 검증 시나리오 및 명령어 (Validation Scenarios)

### 시나리오 1: 일반 대화 호출 예제 실행 (sample_01_chat.py)
```bash
uv run python samples/sample_01_chat.py
```
**기대 결과**:
- 8081 포트 `/v1/chat/completions` 요청 성공 (`200 OK`)
- 콘솔에 LLM 모델 답변 텍스트 정상 출력

---

### 시나리오 2: 동적 모델 & 파라미터 제어 예제 실행 (sample_02_model_params.py)
```bash
uv run python samples/sample_02_model_params.py
```
**기대 결과**:
- `temperature`, `max_tokens`, `stop` 등의 변경 파라미터가 반영된 모델 응답 출력

---

### 시나리오 3: BGE M3 임베딩 호출 예제 실행 (sample_03_embedding.py)
```bash
uv run python samples/sample_03_embedding.py
```
**기대 결과**:
- 8090 포트 `/v1/embeddings` 요청 성공 (`200 OK`)
- 1024차원 벡터 및 상위 수치 요소 출력

---

### 시나리오 4: BGE Reranker v2 M3 호출 예제 실행 (sample_04_reranking.py)
```bash
uv run python samples/sample_04_reranking.py
```
**기대 결과**:
- 8091 포트 `/v1/embeddings` 또는 `/rerank` 요청 성공 (`200 OK`)
- 문맥 관련도 추출 또는 벡터 결과 배열 출력

---

### 시나리오 5: Pydantic 구조화 출력 추출 예제 실행 (sample_05_structured_output.py)
```bash
uv run python samples/sample_05_structured_output.py
```
**기대 결과**:
- `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py` 스키마 기반 JSON 응답 수신
- Pydantic 객체 파싱 100% 통과 및 파싱 결과 출력

---

### 시나리오 6: 전체 회귀 테스트 수행
```bash
uv run pytest
```
**기대 결과**: 모든 단위/통합 테스트 수트 100% Green Pass
