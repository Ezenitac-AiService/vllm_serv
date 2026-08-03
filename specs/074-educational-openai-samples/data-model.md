# Data Model & Educational Sample Structure: 074-educational-openai-samples

## Sample Scripts Map

| File Path | Target Persona Focus | Primary Educational Concept | Key API Endpoint |
| :--- | :--- | :--- | :--- |
| `samples/common.py` | Instructor, Trainee | 서버 호스트 자동 감지 & 터미널 헤더 출력 | `/health` |
| `samples/sample_01_chat.py` | Trainee, Professor | OpenAI 공식 SDK (`OpenAI`) 및 HTTP 대화 API 호출 | `/v1/chat/completions` |
| `samples/sample_02_model_params.py` | Instructor, Trainee | 모델 파라미터 제어 (`temperature`, `top_p`, `stop`) | `/v1/chat/completions` |
| `samples/sample_03_embedding.py` | Trainee, Evaluator | BGE M3 1024차원 임베딩 벡터 추출 | `/v1/embeddings` |
| `samples/sample_04_reranking.py` | Trainee, Evaluator | BGE Reranker v2 M3 문서 관련도 재순위화 | `/rerank` |
| `samples/README.md` | Trainee, Evaluator | 비전공자 훈련생용 5분 완성 실습 가이드 | N/A |

## Structural Rules

1. **No Pydantic Dependency**: 파이덴틱 모델 정의 배제, 파이썬 기본 딕셔너리(`dict`) 사용.
2. **Line-by-Line Korean Comments**: 모든 주요 구문에 라인별 친절한 한글 주석 포함.
3. **Clean Output**: 터미널 실행 시 결과 답변, 사용 토큰 지표, 생성 정지 사유 시각화 출력.
