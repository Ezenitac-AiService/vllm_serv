# Quickstart Guide: 레거시 추출 스크립트 자체 서버 LLM 연동 검증 (036-legacy-extraction-llm)

본 가이드는 레거시 파이썬 스크립트(`.legacy/ATEAM_ExtractionItem.py`, `.legacy/BTEAM_ExtractionItem.py`)가 자체 개발 플랫폼 서버 LLM(`10.0.0.41:8000`) 엔드포인트를 통해 정상 구동하는지 검증하는 시나리오를 설명합니다.

## 사전 준비 (Prerequisites)

- 자체 서버 vLLM 서비스 구동 (기본 포트: `http://10.0.0.41:8000/v1`)
- 파이썬 가상환경 동기화 완료 (`uv sync`)

## 1. ATEAM 주식 댓글 감성 추출 검증

환경 변수 지정 또는 기본 엔드포인트(`http://10.0.0.41:8000/v1`) 접속으로 스크립트를 독립 실행합니다.

```bash
# 기본 실행 (http://10.0.0.41:8000/v1 자동 바인딩)
uv run python .legacy/ATEAM_ExtractionItem.py

# 환경 변수로 엔드포인트 및 모델 지정 후 실행
OPENAI_BASE_URL="http://10.0.0.41:8000/v1" MODEL_NAME="gemma4-e2b" uv run python .legacy/ATEAM_ExtractionItem.py

```

### 기대 결과 (Expected Outcome)
- 외부 Groq API 키 경고 없이 `[시스템] 종목 토론방 댓글 타임라인 감성 분석을 시작합니다...` 출력
- `[최종 추출 결과 1 JSON]` 문단 아래 `speaker`, `category`, `sentiment`, `target`, `sentence`, `refined_sentence` 키가 포함된 valid JSON 배열 출력

## 2. BTEAM 음식점 리뷰 감성 추출 검증

```bash
# BTEAM 스크립트 독립 실행
uv run python .legacy/BTEAM_ExtractionItem.py
```

### 기대 결과 (Expected Outcome)
- `[시스템] 리뷰 감성 문장 분석을 시작합니다...` 출력
- `[최종 추출 결과 1 JSON]` 문단 아래 리뷰 파싱 결과 정상 반환
- 서브스트링 오매칭 차단 테스트(`"마라"` vs `"고구마라떼"`)에서 0점 차단 성공 메시지 및 정상 추출 결과 확인

## 3. 단위 테스트 수트 실행

```bash
uv run pytest tests/unit/test_legacy_extraction_llm.py -v
```

### 기대 결과 (Expected Outcome)
- 로컬 LLM 클라이언트 설정, Mock 엔드포인트 응답 파싱, 예외 처리 테스트 100% 통과 (`PASSED`)
