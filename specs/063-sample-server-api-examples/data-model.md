# Data Model: vllm_serv API 예제 샘플 스크립트 작성 (sample_01 ~ sample_05)

**Feature**: `063-sample-server-api-examples`

## Entities & Data Schemas

### 1. Sample Script Configuration Entity (`SampleScriptConfig`)
샘플 스크립트 실행 시 사용되는 서버 엔드포인트 및 호출 옵션 데이터 모델.

- **`server_host`**: `str` (기본값: `http://127.0.0.1`)
- **`llm_port`**: `int` (기본값: `8081`)
- **`embedding_port`**: `int` (기본값: `8090`)
- **`rerank_port`**: `int` (기본값: `8091`)
- **`default_model_id`**: `str` (기본값: `qwen3.5-4b`)
- **`embedding_model_id`**: `str` (기본값: `bge-m3`)
- **`rerank_model_id`**: `str` (기본값: `bge-reranker-v2-m3`)

---

### 2. Legacy Extraction Schemas (Imported from `.legacy/`)

#### A. ATEAM Stock Analysis Schema (`ATEAM_ExtractionItem.py`)
- **Class**: `StockAnalysisItem`
- **Fields**:
  - `stock_name`: `str` (종목명)
  - `target_price`: `int` (목표가)
  - `investment_opinion`: `str` (매수/매도/중립)
  - `key_catalysts`: `List[str]` (주요 수혜 요인 모음)

#### B. BTEAM Review Sentiment Schema (`BTEAM_ExtractionItem.py`)
- **Class**: `ReviewSentimentItem`
- **Fields**:
  - `product_name`: `str` (제품명)
  - `sentiment_score`: `float` (감성 점수 0.0 ~ 1.0)
  - `is_positive`: `bool` (긍정 여부)
  - `extracted_keywords`: `List[str]` (핵심 키워드 모음)
