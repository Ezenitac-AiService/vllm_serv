# Quickstart: 성능 비교 테스트 (Performance Benchmark)

본 가이드는 다운로드된 3종의 QAT GGUF 모델을 로드하여, 단계별 프롬프트 주입을 통해 VRAM과 생성 속도를 측정하는 방법입니다.

## Prerequisites

1. NVIDIA GTX 1080 Ti 등 충분한 VRAM이 확보된 GPU 환경
2. `python-dotenv` 패키지 설치 완료 (기존 `requirements.txt`에 추가됨)
3. `.env` 파일 내에 Hugging Face 접근 토큰 세팅:
   ```env
   HF_TOKEN=hf_your_token_here
   ```

## 1. 모델 다운로드
`.env`의 토큰을 이용해 모델을 자동으로 내려받습니다.
```bash
export PYTHONPATH=.
python3 src/scripts/download_models.py
```

## 2. 벤치마크 테스트 실행
목업 데이터 없이 실제 모델을 적재하여 Short, Medium, Long 프롬프트로 벤치마크를 수행합니다.
```bash
export PYTHONPATH=.
python3 src/scripts/benchmark.py
```

## Expected Outcomes
터미널 출력 및 로그를 통해 다음과 같은 결과가 나타나야 합니다.
- 각 모델 별로 로딩 시간 및 피크 VRAM(MB) 출력
- 프롬프트 길이(Short, Medium, Long)별 응답 속도(TPOT) 출력
- 11GB VRAM을 초과하여 OOM이 발생할 경우 예외 처리되며 `OOM_FAILED` 기록
