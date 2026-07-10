# Quickstart & Validation Guide

## Prerequisites
- Linux OS with NVIDIA GPU (GTX 1080 Ti 11GB VRAM)
- Python 3.11+
- CUDA Toolkit 12.x 설치 (llama-cpp-python 빌드용)

## Setup
1. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
   ```
2. GGUF 모델 가중치 다운로드 (자동 스크립트 제공):
   ```bash
   python scripts/download_models.py
   ```

## Scenario 1: 성능 벤치마크 (PoC)
```bash
python scripts/benchmark.py
```
**Expected Outcome**: 
2B, 4B, 12B 세 모델이 순차적으로 로드되며 각각의 VRAM 점유량(MB)과 생성 속도(TPOT ms/token)를 콘솔에 표 형태로 출력합니다.

## Scenario 2: 서버 구동 및 텍스트 생성 테스트
1. 메인 서버 구동:
   ```bash
   python -m src.server --model_id gemma4-12b
   ```
2. 텍스트 생성 검증 (별도 터미널):
   ```bash
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "안녕하세요!"}]}'
   ```
**Expected Outcome**: 
정상적인 텍스트 응답이 생성되며 VRAM 에러(OOM)가 발생하지 않아야 합니다.

## Scenario 3: 런타임 모델 전환 테스트
1. 모델 전환 API 호출:
   ```bash
   curl -X POST http://localhost:8000/api/models/switch \
     -H "Content-Type: application/json" \
     -d '{"model_id": "gemma4-4b"}'
   ```
**Expected Outcome**: 
응답 코드가 `200 OK`로 반환되고, 서버 로그에서 기존 모델 Unload 및 새 모델 Load가 확인되어야 합니다. 전환 이후 생성 요청은 4B 모델로 수행됩니다.
