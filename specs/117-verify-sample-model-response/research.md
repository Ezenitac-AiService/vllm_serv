# Research & Technical Decisions: sample 예제 스크립트 호출 모델 대 응답 모델 일치성 검증 및 하드코딩 제거

**Feature**: `verify-sample-model-response`  
**Feature Directory**: `specs/117-verify-sample-model-response`  

---

## 1. API Gateway MOCK 및 역방향 프록시 응답 페이로드의 모델 ID 동적 반환

### Decision
`src/api/routes/inference_api.py`에서 `MOCK_LLAMA_SERVER=1` 모드 및 역방향 프록시 응답 처리 시, 요청 페이로드의 `model` 파라미터를 파싱하여 응답 JSON 페이로드의 `model` 필드에 동적으로 대입하여 반환하도록 보장한다.

### Rationale
- `MOCK_LLAMA_SERVER=1` 모드로 단위/통합 테스트 구동 시, 요청된 모델 ID가 `qwen3.5-2b` 혹은 `gemma4-e4b`인 경우에도 MOCK 응답에 하드코딩된 모델명이 반환되면 클라이언트 단에서 모델 불일치 오류로 오진할 수 있다.
- 클라이언트 및 `sample/` 실습 스크립트가 요청된 모델 ID와 응답받은 모델 ID의 100% 일치성을 상시 검증할 수 있도록 백엔드 응답 정합성을 보장한다.

### Alternatives Considered
- *백엔드 C++ llama-server 응답만 신뢰*: MOCK 테스트 환경이나 특수 프록시 응답 시 `model` 필드가 누락되거나 기본값으로 덮어써질 수 있어 기각함.

---

## 2. sample/ 폴더 설정 단일 진실 출처 (Single Source of Truth - config.json) 적용

### Decision
`sample/` 폴더 내의 모든 파이썬 파일(`sample/common.py`, `sample_*.py`, `openai_*.py` 등)의 소스 코드 상에 직접 기술되어 있던 하드코딩된 IP 주소(`192.168.0.175`, `192.168.0.80` 등), 포트 번호(`8081`, `8090`, `8091`), 가용 모델 목록, 타임아웃, 더미 목업 텍스트를 전면 제거한다.
모든 설정과 백업 리스트는 `sample/config.json`에서 정의하고, `sample/common.py`의 `load_sample_config()`를 통해 100% 동적으로 로드하도록 정제한다.

### Rationale
- 개발 플랫폼 IP(`10.0.0.41`)와 실습 배포 타겟 IP(`192.168.0.175`) 간의 설정 교체가 코드 수정 없이 `config.json` 및 환경변수(`SERVER_HOST`) 조절만으로 가능해진다.
- 하드코딩 매직 넘버 및 하드코딩된 더미 목업을 제거하여 이식성 및 유지보수성을 극대화한다.

### Alternatives Considered
- *개별 파이썬 파일 상단에 상수 정의*: 파일마다 호스트/포트/모델 리스트가 파편화되어 변경 시 오작동 위험이 높으므로 기각함.

---

## 3. 실습 스크립트 콘솔 리포트 내 모델 교차 검증 시각화

### Decision
`sample/common.py`의 `print_performance_summary()` 헬퍼 함수 및 샘플 스크립트 루프에서, 수신된 응답 객체의 `model` 필드(`res.get("model")` 또는 `comp.model`)를 요청된 `model` ID와 비교 검증하는 로직을 수록한다.
일치 시 `[모델 검증: 요청(qwen3.5-4b) == 응답(qwen3.5-4b) ✅]` 태그를 성능 요약에 출력하고, 불일치 시 `❌ [모델 불일치 오류]` 경고를 출력하도록 구성한다.

### Rationale
- 교육 참가자 및 사용자가 실습 스크립트 실행 시 모델 핫스왑 결과가 요청한 모델과 100% 일치하여 서빙되었음을 눈으로 직접 확인할 수 있다.

---

## 4. 자동화 단위 테스트 수록 (tests/unit/test_sample_model_switch.py)

### Decision
`tests/unit/test_sample_model_switch.py`에 다음 두 가지 테스트 단정문(assert)을 추가한다:
1. `sample/` 폴더 내 소스 파이썬 파일 전수 검사를 통해 하드코딩된 IP 주소/포트/더미 목업 텍스트 존재 여부를 정규식으로 검사 (0건 검증).
2. httpx 및 OpenAI SDK 샘플 루프 수행 시 요청 모델 ID 대 응답 모델 ID의 100% 일치성 검증.

### Rationale
- 헌장 원칙 II(Real-Integration TDD) 및 원칙 VII(Mandatory Regression Testing)에 따라 지속적인 CI/CD 회귀 검증 체계를 완성함.
