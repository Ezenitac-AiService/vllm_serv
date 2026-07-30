# Data Model & Schema Specification: 임베딩 및 리랭커 모델 서빙 (053-embedding-reranker-model-serving)

## 1. Model Catalog Schema Extensions (`config/model_catalog.json`)

### `ModelCatalogEntry` (Pydantic v2 Model)

```python
class TaskTypeEnum(str, Enum):
    LLM = "llm"
    EMBEDDING = "embedding"
    RERANK = "rerank"

class ModelCatalogEntry(BaseModel):
    name: str
    repo_id: str
    filename: str
    clip_filename: Optional[str] = None
    target_dir: str
    model_path: str
    clip_path: Optional[str] = None
    chat_template: Optional[str] = None
    default_n_ctx: int = 4096
    vram_est_mb: int
    requires_mmproj: bool = False
    quant_type: str
    size_gb: float
    task_type: TaskTypeEnum = Field(default=TaskTypeEnum.LLM, description="모델 작업 유형 (llm/embedding/rerank)")
    default_port: Optional[int] = Field(default=None, description="기본 바인딩 백엔드 포트")
```

### New Entries in `config/model_catalog.json`

```json
{
  "bge-m3": {
    "name": "BGE M3 (Q8_0 Embedding)",
    "repo_id": "ggml-org/bge-m3-Q8_0-GGUF",
    "filename": "bge-m3-q8_0.gguf",
    "clip_filename": null,
    "target_dir": "models/bge-m3",
    "model_path": "models/bge-m3/bge-m3-q8_0.gguf",
    "clip_path": null,
    "chat_template": null,
    "default_n_ctx": 8192,
    "vram_est_mb": 605,
    "requires_mmproj": false,
    "quant_type": "q8_0",
    "size_gb": 0.6,
    "task_type": "embedding",
    "default_port": 8090
  },
  "bge-reranker-v2-m3": {
    "name": "BGE Reranker v2 M3 (Q8_0 Cross-Encoder)",
    "repo_id": "klnstpr/bge-reranker-v2-m3-Q8_0-GGUF",
    "filename": "bge-reranker-v2-m3-q8_0.gguf",
    "clip_filename": null,
    "target_dir": "models/bge-reranker-v2-m3",
    "model_path": "models/bge-reranker-v2-m3/bge-reranker-v2-m3-q8_0.gguf",
    "clip_path": null,
    "chat_template": null,
    "default_n_ctx": 8192,
    "vram_est_mb": 606,
    "requires_mmproj": false,
    "quant_type": "q8_0",
    "size_gb": 0.6,
    "task_type": "rerank",
    "default_port": 8091
  }
}
```

---

## 2. Server Config Extensions (`config/server_config.json`)

### `ServerConfig` Additions

```python
class ServerConfig(BaseModel):
    # ... existing fields ...
    embedding_backend_port: int = Field(default=8090, description="임베딩 백엔드 llama-server 바인딩 포트")
    rerank_backend_port: int = Field(default=8091, description="리랭커 백엔드 llama-server 바인딩 포트")
    embedding_enabled: bool = Field(default=True, description="임베딩 인스턴스 자동 시작 여부")
    rerank_enabled: bool = Field(default=True, description="리랭커 인스턴스 자동 시작 여부")
```

---

## 3. API DTO Schemas (Pydantic v2)

### OpenAI Embedding API (`POST /v1/embeddings`)

```python
class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]] = Field(..., description="임베딩할 입력 텍스트 또는 텍스트 목록")
    model: Optional[str] = Field(default="bge-m3", description="임베딩 모델 식별자")
    encoding_format: str = Field(default="float", description="반환 인코딩 포맷 (float/base64)")

class EmbeddingData(BaseModel):
    object: str = "embedding"
    index: int
    embedding: List[float]

class EmbeddingUsage(BaseModel):
    prompt_tokens: int
    total_tokens: int

class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: EmbeddingUsage
```

### Rerank API (`POST /v1/rerank`)

```python
class RerankRequest(BaseModel):
    query: str = Field(..., description="검색 쿼리 텍스트")
    documents: List[str] = Field(..., description="재정렬할 문서 목록")
    model: Optional[str] = Field(default="bge-reranker-v2-m3", description="리랭커 모델 식별자")
    top_n: Optional[int] = Field(default=None, description="상위 N개 결과 필터링")

class RerankResult(BaseModel):
    index: int = Field(..., description="원래 원본 documents 배열에서의 인덱스")
    relevance_score: float = Field(..., description="유사도/관련도 점수 (float)")
    document: Optional[Dict[str, str]] = Field(default=None, description="문서 객체 (선택사항)")

class RerankUsage(BaseModel):
    total_tokens: int

class RerankResponse(BaseModel):
    results: List[RerankResult]
    model: str
    usage: RerankUsage
```
