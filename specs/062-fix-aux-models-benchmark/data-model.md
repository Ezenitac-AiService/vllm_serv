# Data Model & Schema Definitions: 보조 모델 및 벤치마크 복원

**Feature**: `062-fix-aux-models-benchmark`
**Created**: 2026-07-31

## 1. Entities & Schema Definitions

### 1.1 `ModelTaskType` (Enum)
- `LLM`: Causal Language Model (`qwen3.5-4b`, `gemma4-e2b`, etc.)
- `EMBEDDING`: Vector Embedding Model (`bge-m3`)
- `RERANK`: Cross-Encoder Reranking Model (`bge-reranker-v2-m3`)

### 1.2 `EmbeddingInferenceRequest`
```json
{
  "input": "삼전 7만전자 뚫어?",
  "model": "bge-m3"
}
```

### 1.3 `EmbeddingInferenceResponse`
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.012, -0.045, "..."],
      "index": 0
    }
  ],
  "model": "bge-m3",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8
  }
}
```

### 1.4 `RerankInferenceRequest`
```json
{
  "query": "삼전 실적 현황",
  "documents": [
    "3분기 실적 저조함",
    "반도체 업황 수혜 가능"
  ],
  "model": "bge-reranker-v2-m3"
}
```

### 1.5 `CoLoadingServiceStatus`
```json
{
  "main_llm": {
    "model_id": "qwen3.5-4b",
    "port": 8081,
    "status": "READY"
  },
  "embedding": {
    "model_id": "bge-m3",
    "port": 8090,
    "status": "READY"
  },
  "reranker": {
    "model_id": "bge-reranker-v2-m3",
    "port": 8091,
    "status": "READY"
  },
  "is_co_loaded": true
}
```

---

## 2. Validation & Invariants

1. **Embedding Dimension Standard**: `bge-m3` 생성 벡터 차원은 Float32 배열 1024차원(또는 모델 고유 차원)으로 비어있지 않아야 함.
2. **Process Independence**: 복원된 백그라운드 프로세스는 PPID(부모 PID) 1 (init/systemd) 혹은 파이썬 부모 프로세스와 완전히 분리(Detached)된 PID 구조를 가져야 함.
