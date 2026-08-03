# Phase 0 Research: AI 서비스 개발자 교육용 OpenAI API 표준 샘플 리팩토링 설계

## Overview

본 연구 문서에서는 비전공자 훈련생을 위한 `samples/` 폴더 내 교육용 스크립트 리팩토링 방안을 다룹니다. 기존 스크립트에 포함된 Pydantic 모델 정의 및 복잡한 HTTP 커스텀 추상화를 제거하고, 표준 파이썬 딕셔너리(`dict`) 및 OpenAI 공식 파이썬 라이브러리(`from openai import OpenAI`)를 기반으로 한 직관적 인터페이스 설계를 결정합니다.

## Technical Decisions & Rationale

### Decision 1: Pydantic 제거 및 파이썬 기본 딕셔너리(`dict`) 구조 도입

- **Rationale**:
  AI 서비스 개발자 양성과정의 비전공자 훈련생에게 Pydantic `BaseModel` 클래스 선언이나 타입 검증은 불필요한 인지 부하(Cognitive Load)를 발생시킵니다. OpenAI REST API 데이터 규격을 직관적인 파이썬 딕셔너리로 다룸으로써 10분 이내에 API 호출 개념을 습득하게 합니다.

- **Implementation**:
  ```python
  # 기존: Complex Pydantic model instantiation
  # 변경: Straightforward Python dict
  payload = {
      "model": "qwen3.5-4b",
      "messages": [
          {"role": "system", "content": "친절한 AI 어시스턴트입니다."},
          {"role": "user", "content": "안녕하세요!"}
      ],
      "temperature": 0.7
  }
  ```

---

### Decision 2: OpenAI 공식 SDK 및 `httpx`/`requests` 호환성 이중 제시

- **Rationale**:
  실무 현장에서는 공식 SDK(`openai.OpenAI`)와 일반 HTTP 라이브러리(`httpx`/`requests`)가 모두 쓰입니다. `sample_01_chat.py`에서 두 방식을 명확히 대조하여 제시함으로써 학습 효과를 극대화합니다.

---

### Decision 3: 라인별 한글 친절 주석 및 표준 콘솔 출력 구성

- **Rationale**:
  비전공자 훈련생이 코드를 복사해서 실행(`uv run python samples/sample_01_chat.py`)했을 때, 생성된 답변과 사용 토큰 지표가 한눈에 들어오는 터미널 출력을 제공합니다.

---

### Decision 4: Zero-Mock 원칙에 부합하는 실물 `vllm_serv` 서빙 연동

- **Rationale**:
  헌법 II/III조에 따라 가짜 목업 응답 대신 실제 `vllm_serv` 백엔드 서버(8081 Chat, 8090 Embedding, 8091 Reranker)와 통신하여 100% 그린으로 작동함을 실측 검증합니다.
