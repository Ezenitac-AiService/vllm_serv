# Quickstart & Real Validation Guide: 12개 실습 예제 수트 및 uv 복원 검증

**Feature Branch**: `088-openai-sdk-samples`  
**Date**: 2026-08-03

---

## 1. 사전 전제조건 (Prerequisites)

1. 파이썬 가상환경 관리자 `uv`가 환경에 설치되어 있어야 합니다. (미설치 시 `pip install uv` 또는 curl 가이드 참조)
2. vllm_serv 백그라운드 서빙 서버가 가동 중이어야 합니다 (`./start_server.sh`).

---

## 2. 1단계: 가상환경 100% 원복 (`uv sync`)

`.venv` 디렉토리가 없는 클린 배포 환경에서 다음 명령어를 실행하여 의존성 패키지를 즉시 원복합니다.

```bash
# 1. 가상환경 패키지 동기화 및 원복
uv sync

# 2. 패키지 정합성 확인
uv run python -c "import openai, httpx, pydantic; print('✅ uv 가상환경 복원 성공!')"
```

---

## 3. 2단계: 12개 실습 스크립트 전수 실행 실측 검증

### (1) 일반 대화 (Chat Completions) 1:1 비교
```bash
# REST API (httpx) 버전 실행
uv run python samples/sample_01_chat.py

# OpenAI SDK 버전 실행
uv run python samples/openai_01_chat.py
```

### (2) 모델 제어 파라미터 1:1 비교
```bash
uv run python samples/sample_02_model_params.py
uv run python samples/openai_02_model_params.py
```

### (3) 단일/배치 텍스트 임베딩 수치 벡터 1:1 비교
```bash
uv run python samples/sample_03_embedding.py
uv run python samples/openai_03_embedding.py
```

### (4) BGE Reranker v2 M3 문서 관련도 재순위화 1:1 비교
```bash
uv run python samples/sample_04_reranking.py
uv run python samples/openai_04_reranking.py
```

### (5) 단일 Pydantic 구조화 응답 1:1 비교
```bash
uv run python samples/sample_05_structured_output.py
uv run python samples/openai_05_structured_output.py
```

### (6) [신설] 배치 Pydantic 구조화 응답 1:1 비교
```bash
uv run python samples/sample_06_structured_output_batch.py
uv run python samples/openai_06_structured_output_batch.py
```

---

## 4. 3단계: 서비스 플랫폼 IP 동적 변경 검증

서비스 플랫폼 IP(`192.168.0.80`)로 실습 시 환경 변수로 오버라이드하여 원격 통신을 검증합니다.

```bash
# 환경 변수 오버라이드로 서비스 플랫폼 IP 연결 테스트
SERVER_HOST=http://192.168.0.80 uv run python samples/openai_01_chat.py
```

---

## 5. 4단계: 자동화 회귀 수트 실측 검증 (`pytest`)

```bash
# 전체 회귀 검증 수트 가동
uv run pytest tests/unit/test_samples.py -v
```

**예상 결과**: 12개 스크립트에 대한 회귀 검증 테스트 케이스 100% Green Pass.
