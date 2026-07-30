# Data Model: 레거시 추출 스크립트 자체 서버 LLM 연동 전환 (036-legacy-extraction-llm)

## Entities & Data Schemas

### 1. LocalLLMClientConfig (로컬 LLM 클라이언트 설정)

자체 서버 vLLM 엔드포인트 연결을 구성하는 데이터 구조입니다.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `base_url` | `str` | Yes | `http://10.0.0.41:8000/v1` | 서버 할당 IP 기반 OpenAI 호환 vLLM API 주소 (환경 변수 `OPENAI_BASE_URL` 또는 `VLLM_API_BASE` 오버라이드 가능) |
| `api_key` | `str` | Yes | `"EMPTY"` | 로컬 LLM 인증용 키 (환경 변수 `OPENAI_API_KEY`) |
| `model_name` | `str` | Yes | `qwen3.5-2b` | 추론 대상 모델명 (`gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 지원) |

| `temperature` | `float` | No | `0.1` | 생성 결과의 결정론적 파싱을 위한 낮은 온동 값 |

---

### 2. StockCommentSentimentItem (주식 댓글 감성 항목 데이터)

`.legacy/ATEAM_ExtractionItem.py`에서 파싱되어 반환되는 데이터 구조입니다.

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `speaker` | `str` | 작성자 닉네임 또는 `"익명"` | 댓글 작성자 화자 |
| `category` | `str` | `"실적/재무"`, `"매수/매도 의도"`, `"차트/기술분석"`, `"뉴스/호재·악재"`, `"경영진/주주가치"` | 5대 투자 카테고리 |
| `sentiment` | `str` | `"매수/긍정"`, `"매도/부정"`, `"중립"` | 3대 투자 감성 |
| `target` | `str` | 정식 종목명 (예: `"삼성전자"`, `"SK하이닉스"`) | 유의어/지시어가 복원된 종목 대상 |
| `sentence` | `str` | 추출된 원문 댓글 문장 | 분석 원문 문장 |
| `refined_sentence` | `str` | `"[정식종목명] ..."` 포맷 문장 | 다운스트림 감성 모델 입력용 완결형 정제문 |

---

### 3. ReviewSentimentItem (음식점 리뷰 감성 항목 데이터)

`.legacy/BTEAM_ExtractionItem.py`에서 파싱되어 반환되는 데이터 구조입니다.

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `category` | `str` | `"맛"`, `"양"`, `"가격"`, `"청결"`, `"친절도"` | 5대 리뷰 카테고리 |
| `target` | `str` | 구체적 메뉴/대상 명사 (예: `"크림 파스타"`, `"직원"`) | 맥락이 복원된 평가 대상 |
| `sentence` | `str` | 추출된 원문 리뷰 문장 | 분석 원문 문장 |
| `refined_sentence` | `str` | `"[복원대상] ..."` 포맷 문장 | 감성 모델 입력 전용 완성형 정제 문장 |
