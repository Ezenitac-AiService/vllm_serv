# Data Model & Schema Specification: 신규 스펙의 Seed Pack 및 setup.sh 동기화 반영 (054-seedpack-setup-sync)

**Feature Branch**: `054-seedpack-setup-sync`
**Date**: 2026-07-31

---

## 1. Firewall Port Specification (`FirewallPortConfig`)

OS 방화벽 자동 개방 및 복구 스크립트에 적용되는 4개 멀티 백엔드 서비스 포트 규격입니다.

| Port | Service Component | Description | Backend Process |
|------|-------------------|-------------|-----------------|
| `8081` | REST / Dashboard API | FastAPI 역방향 프록시 및 대시보드 웹 UI | `src/api/server.py` |
| `8089` | Resident LLM Engine | Qwen 3.5 4B 기본 상주 LLM 추론 엔진 | `llama-server` (port 8089) |
| `8090` | Embedding Engine | BGE-M3 1024차원 밀집 벡터 임베딩 엔진 | `llama-server --embedding` (port 8090) |
| `8091` | Reranker Engine | BGE-Reranker-v2-M3 Cross-Encoder 리랭킹 엔진 | `llama-server --reranking` (port 8091) |

---

## 2. Project Required File Verification Specification (`RequiredFileList`)

`scripts/setup.sh` 실행 시 존재 여부를 검증하는 필수 구성 파일 엔트리입니다.

```bash
REQUIRED_FILES=(
    "pyproject.toml"
    "config/model_catalog.json"
    "config/server_config.json"
    "src/api/server.py"
    "src/core/process_manager.py"
    "src/core/llama_manager.py"
    "src/core/auxiliary_manager.py"  # 054 스펙에 의해 추가됨
    "scripts/benchmark_quality.py"
    "scripts/make_seed_pack.sh"
)
```

---

## 3. Seed Database Record Specification (`SeedDatabaseRecord`)

`scripts/seed_db.py`에 수록되는 엔드포인트별 샘플 시드 메트릭 데이터 엔티티 스키마입니다.

### Data Attributes

- `api_key` (TEXT): 사용 API 키 (예: `sk-vllm-dev-demo1`, `sk-vllm-mobile-app`)
- `endpoint` (TEXT): API 경로 (예: `/v1/chat/completions`, `/v1/embeddings`, `/v1/rerank`)
- `status_code` (INTEGER): HTTP 응답 코드 (200, 401 등)
- `prompt_tokens` (INTEGER): 프롬프트 토큰 수
- `completion_tokens` (INTEGER): 생성 토큰 수 (임베딩/리랭킹 시 0)
- `ttft_ms` (REAL): 첫 토큰 생성 지연시간 ms
- `tps` (REAL): 초당 생성 토큰 수
- `is_error` (BOOLEAN): 에러 발생 여부 (0/1)
- `prompt_text` (TEXT): 요청 입력 프롬프트 / 텍스트
- `completion_text` (TEXT): 응답 출력 / 텍스트 / 시리얼라이즈된 메트릭 결과

### Sample Seed Records Structure

```python
SEED_METRIC_RECORDS = [
    # 1. LLM Chat Completion Sample
    {
        "api_key": "sk-vllm-dev-demo1",
        "endpoint": "/v1/chat/completions",
        "status_code": 200,
        "prompt_tokens": 18,
        "completion_tokens": 42,
        "ttft_ms": 38.5,
        "tps": 34.2,
        "is_error": False,
        "prompt_text": "Write a python quicksort function with inline comments.",
        "completion_text": "def quicksort(arr): ..."
    },
    # 2. Embedding Vector Sample (NEW in 054)
    {
        "api_key": "sk-vllm-dev-demo1",
        "endpoint": "/v1/embeddings",
        "status_code": 200,
        "prompt_tokens": 14,
        "completion_tokens": 0,
        "ttft_ms": 12.4,
        "tps": 0.0,
        "is_error": False,
        "prompt_text": "BGE-M3 Dense Vector Embedding Sample Input",
        "completion_text": "[Dense Vector float array (1024 dims) generated successfully]"
    },
    # 3. Reranker Cross-Encoder Sample (NEW in 054)
    {
        "api_key": "sk-vllm-mobile-app",
        "endpoint": "/v1/rerank",
        "status_code": 200,
        "prompt_tokens": 32,
        "completion_tokens": 0,
        "ttft_ms": 18.2,
        "tps": 0.0,
        "is_error": False,
        "prompt_text": "Query: BGE-Reranker test | Docs: ['doc1', 'doc2']",
        "completion_text": "[Relevance scores: doc1=0.95, doc2=0.12]"
    }
]
```
