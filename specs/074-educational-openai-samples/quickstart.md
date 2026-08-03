# Quickstart & Verification Guide: Educational Sample Scripts

본 가이드는 `samples/` 폴더 내 샘플 스크립트들이 Pydantic 없이 비전공자 훈련생 눈높이에 맞게 정상 작동하는지 실측 검증하는 가이드입니다.

---

## 1. 사전 준비 (Prerequisites)

- `vllm_serv` 메인 데몬 실행 확인:
  ```bash
  ./status_server.sh
  ```

---

## 2. 교육용 샘플 스크립트 실행 실측 검증

```bash
# 1. 기본 Chat Completions 샘플 실행
uv run python samples/sample_01_chat.py

# 2. 파라미터 제어 샘플 실행
uv run python samples/sample_02_model_params.py

# 3. 임베딩 샘플 실행
uv run python samples/sample_03_embedding.py

# 4. 리랭커 샘플 실행
uv run python samples/sample_04_reranking.py
```

**기대 결과 (Expected Outcome)**:
- Pydantic 또는 타입 에러 0건.
- 각 스크립트 실행 시 모델 답변, 토큰 사용량, 생성 완료 사유가 시각적으로 깔끔히 출력됨.

---

## 3. 의무적 회귀 테스트 수트 실행 (헌법 VII조)

```bash
uv run pytest
```
