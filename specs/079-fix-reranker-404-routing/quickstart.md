# Quickstart Validation Guide: `079-fix-reranker-404-routing`

**Feature Directory**: [`specs/079-fix-reranker-404-routing`](file:///home/dev/storage/vllm_serv/specs/079-fix-reranker-404-routing)  
**Spec**: [`spec.md`](spec.md) | **Plan**: [`plan.md`](plan.md)  

---

## 1. Validation Scenarios

### Scenario 1: `sample_04_reranking.py` 404 오류 방지 및 200 OK 검증

```bash
uv run python samples/sample_04_reranking.py
```

**Expected Outcome**: 404 Not Found 에러 발생 없이 HTTP 200 OK 및 재순위화 스코어 반환.

---

### Scenario 2: 통합 테스트 수트 실행

```bash
uv run pytest tests/integration/test_reranker_404_routing.py
```

**Expected Outcome**: 100% 테스트 통과 (Green).
