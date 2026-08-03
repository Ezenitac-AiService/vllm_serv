# Data Model: OpenAI API 실습 예제 수트 및 파싱 데이터 엔티티

**Feature Branch**: `088-openai-sdk-samples`  
**Date**: 2026-08-03

---

## 1. Configuration Entity (`samples/config.json`)

실습 예제 스크립트 전수가 참조하는 동적 서빙 포트, IP, 모델명 및 파라미터 엔티티입니다.

```json
{
  "server_host": "http://192.168.0.80",
  "main_port": 8081,
  "embedding_port": 8090,
  "rerank_port": 8091,
  "default_model": "qwen3.5-4b",
  "embedding_model": "bge-m3",
  "rerank_model": "bge-reranker-v2-m3",
  "default_temperature": 0.3,
  "default_max_tokens": 250
}
```

### Attributes
- `server_host` (str): 서비스 플랫폼 또는 로컬 서빙 서버 호스트 URL (`http://192.168.0.80` 또는 `http://127.0.0.1`).
- `main_port` (int): 메인 LLM Chat Completions API 포트 (기본: 8081).
- `embedding_port` (int): BGE M3 임베딩 서빙 포트 (기본: 8090).
- `rerank_port` (int): BGE Reranker v2 M3 서빙 포트 (기본: 8091).
- `default_model` (str): 메인 LLM 서빙 모델명 (`qwen3.5-4b`).
- `embedding_model` (str): 임베딩 모델명 (`bge-m3`).
- `rerank_model` (str): 리랭킹 모델명 (`bge-reranker-v2-m3`).

---

## 2. Chat Completion Request / Response Model

OpenAI SDK `ChatCompletion` 규격 데이터 객체입니다.

```text
[ChatCompletionRequest]
  ├── model: str ("qwen3.5-4b")
  ├── messages: List[Dict[str, str]] (role: "system"|"user"|"assistant", content: str)
  ├── temperature: float (0.0 ~ 2.0)
  ├── max_tokens: int (e.g. 250)
  ├── stop: Optional[List[str]] (e.g. ["\n"])
  └── response_format: Optional[Dict[str, str]] (type: "json_object")

[ChatCompletionResponse]
  ├── id: str
  ├── object: str ("chat.completion")
  ├── choices: List[Choice]
  │     └── Choice
  │           ├── message: Message (role: "assistant", content: str)
  │           └── finish_reason: str ("stop" | "length")
  └── usage: UsageInfo (prompt_tokens, completion_tokens, total_tokens)
```

---

## 3. Embedding Request / Response Model (Single & Batch)

단일 텍스트 및 다중 문장 배치(Batch) 임베딩 벡터 데이터 객체입니다.

```text
[EmbeddingRequest]
  ├── model: str ("bge-m3")
  └── input: List[str] (e.g. ["문장 1"] 또는 ["문장 1", "문장 2", "문장 3"])

[EmbeddingResponse]
  ├── object: str ("list")
  ├── data: List[EmbeddingObject]
  │     └── EmbeddingObject
  │           ├── object: str ("embedding")
  │           ├── index: int (0, 1, 2...)
  │           └── embedding: List[float] (1024차원 수치 벡터)
  └── usage: Dict[str, int]
```

---

## 4. Rerank Request / Response Model

질문(Query)과 후보 문서 배열(Documents) 간의 의미적 관련도 점수 데이터 객체입니다.

```text
[RerankRequest]
  ├── model: str ("bge-reranker-v2-m3")
  ├── query: str
  └── documents: List[str]

[RerankResponse]
  └── results: List[RerankResultItem]
        └── RerankResultItem
              ├── index: int (원래 후보 문서 인덱스)
              └── relevance_score: float (유사도 점수, 예: 0.9542)
```

---

## 5. Pydantic Structured Output Models (Single & Batch)

`sample_05`/`openai_05` 및 `sample_06`/`openai_06`에서 사용되는 Pydantic 정형 데이터 검증 객체입니다.

```python
from pydantic import BaseModel, Field
from typing import List

class StockCommentItem(BaseModel):
    speaker: str = Field(description="작성자 닉네임")
    category: str = Field(description="실적/재무, 매수/매도 의도, 차트/기술분석, 뉴스/호재·악재, 경영진/주주가치 중 하나")
    sentiment: str = Field(description="매수/긍정, 매도/부정, 중립 중 하나")
    target: str = Field(description="복원된 정식 종목명 (예: 삼성전자, SK하이닉스)")
    sentence: str = Field(description="댓글 원문 문장")
    refined_sentence: str = Field(description="정제된 문장")

class StockAnalysisResponse(BaseModel):
    results: List[StockCommentItem]  # 단일 1개 요소 또는 배치 N개 요소 수담기 지원
```
