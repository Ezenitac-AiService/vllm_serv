# Gemma4 QAT Serving API (vLLM / llama.cpp)

이 프로젝트는 NVIDIA GTX 1080 Ti (11GB VRAM) 환경에서 최적화된 Gemma4 양자화 모델(GGUF)을 서빙하기 위해 구축되었습니다. VRAM 한계를 극복하기 위해 `llama-cpp-python` 기반의 텍스트 생성 API와 동적 모델 전환 시스템을 제공합니다.

## 기능

1. **자동화된 모델 벤치마크**: 2B, 4B, 12B 세 가지 양자화 모델을 다운로드하고, 순차적으로 로드하여 VRAM 점유량 및 토큰 생성 속도(TPOT)를 측정합니다.
2. **동적 모델 전환 (Hot-Swap)**: API 호출(`/api/models/switch`)을 통해 서버 재시작 없이 메모리에 올라간 모델을 다른 모델로 안전하게 교체할 수 있습니다.
3. **OpenAI 호환 API 제공**: `/v1/chat/completions` 엔드포인트를 제공하여 기존 LLM 생태계 도구들과 즉시 연동 가능합니다.
4. **OOM 방지 및 안전 장치**: 단일 사용자 환경 및 최대 4K 컨텍스트 제한을 통해 예기치 않은 메모리 부족(Out of Memory) 현상을 방지합니다.

## 설치 (Prerequisites)

- Python 3.11+
- CUDA Toolkit (NVIDIA 드라이버 포함)

```bash
# 가상 환경 세팅 및 패키지 설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# (선택) CUDA 가속 활성화를 위한 llama-cpp-python 재빌드
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

## 빠른 시작 (Quickstart)

### 1. 환경 설정
`.env.example`을 복사하여 `.env` 파일을 만들고 Hugging Face 읽기 토큰을 설정합니다.
```bash
cp .env.example .env
# .env 파일 내 HF_TOKEN=hf_your_token_here 를 실제 토큰으로 변경
```

### 2. 모델 다운로드
`.env`의 토큰을 자동으로 읽어 모델을 다운로드합니다.
```bash
PYTHONPATH=. python3 src/scripts/download_models.py
```

### 3. 성능 평가 (Benchmark)
Short / Medium / 4K Long 한국어 프롬프트로 각 모델의 VRAM 및 TPOT를 측정합니다.
```bash
PYTHONPATH=. python3 src/scripts/benchmark.py
```
*(예상 출력: E2B, E4B, 12B 모델의 로딩 시간, 프롬프트별 VRAM 사용량, TPOT, 그리고 추천 모델이 표시됩니다.)*

### 4. 서버 구동
```bash
PYTHONPATH=. python3 src/api/server.py
```
*(기본 포트: 8000번, 자동 모델 로딩 대기 상태)*

### 5. 모델 전환 API 호출 (예: 4B 로드)
```bash
curl -X POST http://localhost:8000/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_id": "gemma4-4b"}'
```

### 6. 텍스트 생성 API 호출 (OpenAI 규격)
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "양자화(Quantization)에 대해 설명해줘."}],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

## 개발 및 테스트

```bash
# 단위 테스트 (Mock 미사용, 순수 로직 검증)
PYTHONPATH=. pytest tests/unit/ -v

# 통합 테스트 (실제 모델 로드 필요)
PYTHONPATH=. pytest tests/integration/test_model_load.py -v
```
