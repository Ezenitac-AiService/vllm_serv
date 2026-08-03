# Quickstart Validation Guide: `078-fix-samples-and-reranker-503`

**Feature Directory**: [`specs/078-fix-samples-and-reranker-503`](file:///home/dev/storage/vllm_serv/specs/078-fix-samples-and-reranker-503)  
**Spec**: [`spec.md`](spec.md) | **Plan**: [`plan.md`](plan.md)  

---

## 1. Validation Scenarios

### Scenario 1: `samples/common.py` 설정 기반 주소 반환 검증

```bash
# 1. SERVER_HOST 환경변수 오버라이드 테스트
SERVER_HOST="http://10.0.0.41:8081" uv run python -c "from samples.common import get_server_host; print(get_server_host())"
```

**Expected Outcome**: `http://10.0.0.41:8081` 출력

```bash
# 2. samples/config.json 설정 파싱 테스트
cat << 'EOF' > samples/config.json
{
  "server_host": "http://10.0.0.41:8081"
}
EOF
uv run python -c "from samples.common import get_server_host; print(get_server_host())"
```

**Expected Outcome**: `http://10.0.0.41:8081` 출력

---

### Scenario 2: `sample_04_reranking.py` 온디맨드 Reranker 실행 (503 에러 방지 검증)

```bash
uv run python samples/sample_04_reranking.py
```

**Expected Outcome**: 503 Service Unavailable 에러 발생 없이 HTTP 200 OK 수신 및 Reranking 점수 결과 반환.

---

### Scenario 3: 전체 샘플 스크립트 실행 및 회귀 테스트 수트 실행

```bash
uv run python samples/sample_01_chat.py
uv run python samples/sample_02_model_params.py
uv run python samples/sample_03_embedding.py
uv run python samples/sample_04_reranking.py
uv run python samples/sample_05_structured_output.py

uv run pytest tests/integration/test_sample_scripts_and_reranker.py
```

**Expected Outcome**: 5개 샘플 및 테스트 수트 100% 통과 (Green).
