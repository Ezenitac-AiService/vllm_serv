# Data Model: sample_05_structured_output.py의 .legacy 모듈 의존성 제거 및 시드팩 독립성 보장 (071-seed-pack-include-legacy)

## Standalone Structured Output Schema (`samples/sample_05_structured_output.py`)

`samples/sample_05_structured_output.py` 내부에서 외부 모듈 의존 없이 직접 사용하는 Pydantic 데이터 구조입니다.

### Entity: `StockCommentItem`

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `speaker` | `string` | 댓글 작성자 닉네임 |
| `category` | `string` | 댓글 분석 카테고리 (실적/재무, 매수/매도 의도 등) |
| `sentiment` | `string` | 감성 구분 (매수/긍정, 매도/부정, 중립) |
| `target` | `string` | 복원된 정식 종목명 (예: 삼성전자) |
| `sentence` | `string` | 댓글 원문 |
| `refined_sentence` | `string` | 정제된 문장 |

### Entity: `StockAnalysisResponse`

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `results` | `List[StockCommentItem]` | 파싱된 종목 댓글 분석 결과 리스트 |
