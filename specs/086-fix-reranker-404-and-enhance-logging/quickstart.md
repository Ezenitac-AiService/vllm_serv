# Quickstart Guide: Reranker 404 해결 및 예제 실행 가이드

## 검증 시나리오

```bash
# 1. sample_04_reranking.py 예제 실행
uv run samples/sample_04_reranking.py

# Expected Output:
# 📡 [요청 전송] http://10.0.0.41:8081/v1/rerank (모델: bge-reranker-v2-m3)
# ✅ [Reranking 성공] HTTP 200 OK 수신 및 재순위화 점수 출력

# 2. 통합 테스트 수행
uv run pytest tests/integration/test_sample_scripts_and_reranker.py -v
```
