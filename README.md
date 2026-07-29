# ⚡ vllm_serv: Qwen 3.5 & Gemma 4 High-Performance GPU Serving Engine

> **NVIDIA GPU/CUDA 하드웨어 가속 사전 검증, VRAM 100% 레이어 오프로드 실시간 모니터링, 동적 핫스왑(Hot-Swap) 모델 서빙 및 3D 품질-속도-VRAM 종합 평가 파이프라인**

---

## 📌 개요 (Overview)

`vllm_serv`는 단일 NVIDIA GPU(예: GTX 1080 Ti 11GB VRAM) 환경에서 **Qwen 3.5** (2B, 4B, 9B) 및 **Gemma 4** (E2B, E4B, 12B) GGUF 양자화 모델을 최대로 가속하여 서빙하기 위한 차세대 파이프라인 엔진입니다.

CPU-only 전용 바이너리로 인한 성능 저하를 사전에 100% 차단하며, 모델 가중치 및 CLIP 프로젝터의 **GPU VRAM 100% 레이어 오프로딩을 실시간 검증**하여 초당 30~50 tok/s 이상의 고성능 추론 및 OOM(Out of Memory) 방지를 보장합니다.

---

## 🔥 핵심 기능 (Key Features)

### 1. 🛡️ GPU/CUDA 하드웨어 사전 검증 엔진 (`src/core/gpu_detector.py`)
- **3단계 하드웨어 Pre-flight Check**: NVIDIA GPU 존재 여부, CUDA 백엔드 드라이버, `nvcc` 툴킷 버전을 동적으로 감지합니다.
- **CPU Fallback 엄격 차단**: CPU 전용 실행 시도가 감지되거나 CUDA 백엔드 로드 실패 시 `GpuAccelerationError`를 즉각 발생시켜 서빙 개설을 차단하고 상세 트러블슈팅 안내를 제공합니다.

### 2. ⚡ VRAM 100% 레이어 오프로딩 실시간 검증 (`src/core/process_manager.py`)
- **실시간 로그 파싱**: `llama-server` 구동 로그를 파싱하여 모델 전체 레이어 및 CLIP 멀티모달 가중치가 VRAM에 100% 오프로드되었는지 검증합니다.
- **부분 오프로드 에러 차단**: VRAM 부족으로 일부 레이어가 RAM으로 튕겨 나가는 현상 감지 시 `VramOverflowError` (`VRAM_PARTIAL_OFFLOAD_ERROR`) 예외를 던지고 프로세스를 안전 종료합니다.
- **VRAM 해제 무결성 보장**: 모델 언로드/스위칭 시 `nvidia-smi`를 통해 GPU VRAM이 baseline(0MB 잔여) 수준으로 완전 반납되었는지 파싱 후 신규 모델을 개설합니다.
- **실시간 VRAM 오버플로우 방지**: 추론 컨텍스트 확장 시 VRAM 점유율 임계치(기본 95%)를 초과할 위험을 실시간 모니터링(`check_vram_runtime_overflow`)하여 OOM 크래시를 사전 차단합니다.

### 3. 🔄 동적 모델 스위칭 (Hot-Swap) & Asynchronous SSE 브로드캐스팅
- **서버 재시작 없는 핫스왑**: `/api/v1/models/load` 호출만으로 메모리 누수 없이 모델을 즉시 스위칭합니다.
- **실시간 상태 브로드캐스팅**: SSE 엔드포인트(`GET /api/v1/events/stream`)를 통해 GPU 정보, VRAM 점유량, 100% 오프로드 여부(`vram_offloaded_100pct`), 프로세스 상태를 클라이언트에 실시간 스트리밍합니다.

### 4. 🌐 OpenAI 호환 규격 API
- `/v1/chat/completions` 및 `/v1/models` 엔드포인트를 제공하여 기존 LLM 생태계 도구(LangChain, LlamaIndex, OpenAI SDK 등)와 즉시 호환됩니다.

### 5. 📊 3차원 품질-속도-VRAM 교차 벤치마크 (`scripts/benchmark_quality.py`)
- Golden Reference Ground Truth 데이터셋(`src/eval/golden_dataset.json`)을 기반으로 **품질 점수(1~5점)**, **지연시간(TTFT)**, **생성 속도(TPOT tok/s)**, **VRAM 사용량** 및 3D 가성비 지수(Quality/Speed Index, Quality/VRAM Index)를 종합 측정하여 보고서를 마크다운으로 자동 생성합니다.

---

## 🛠️ 기술 스택 및 요구사항 (Tech Stack & Prerequisites)

- **Language/Runtime**: Python 3.12+ (uv 패키지 매니저 사용)
- **Primary Engines**: `llama-cpp-python` (CUDA 12.4 / 13.0), `pydantic` v2, `fastapi`, `httpx`, `pytest`
- **Hardware Requirement**: NVIDIA GPU (GTX 1080 Ti 11GB VRAM 이상 권장), NVIDIA Driver & CUDA Runtime Environment

---

## 🚀 빠른 시작 (Quickstart)

### 1. 패키지 설치 및 환경 세팅

```bash
# uv 환경 동기화
uv sync

# CUDA 가속 지원 llama-cpp-python 재빌드 (필요시)
CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 내 HF_TOKEN 설정 (Hugging Face 가중치 자동 다운로드용)
```

### 3. GPU 가속 사전 검증 및 단위 테스트 실행
```bash
uv run pytest tests/unit/test_gpu_detector.py -v
```

### 4. 서빙 서버 실행

```bash
uv run python -m src.api.server
```
*(기본 포트: 8081, `http://127.0.0.1:8081` 바인딩)*

---

## 📋 API 레퍼런스 (API Reference)

### 1. OpenAI 호환 텍스트 생성 (`POST /v1/chat/completions`)

```bash
curl -X POST http://127.0.0.1:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "GPU VRAM 오프로딩의 장점에 대해 설명해줘."}
    ],
    "temperature": 0.2,
    "max_tokens": 256
  }'
```

### 2. GPU & 서빙 시스템 상태 조회 (`GET /api/v1/status`)

```bash
curl -s http://127.0.0.1:8081/api/v1/status | jq .
```
**응답 예시**:
```json
{
  "state": "READY",
  "current_model": "qwen3.5-4b",
  "vram_total": 24000,
  "vram_used": 3950,
  "gpu_cuda_available": true,
  "vram_offloaded_100pct": true,
  "gpu_info": {
    "device_id": 0,
    "name": "NVIDIA GeForce GTX 1080 Ti",
    "total_vram_mb": 11264,
    "free_vram_mb": 7314,
    "driver_version": "580.173.02",
    "cuda_version": "13.0",
    "is_cuda_available": true
  },
  "offload_status": {
    "model_id": "qwen3.5-4b",
    "total_layers": 28,
    "offloaded_layers": 28,
    "is_fully_offloaded": true,
    "offloaded_vram_mb": 3950
  }
}
```

### 3. 동적 모델 핫스왑 (`POST /api/v1/models/load`)

```bash
curl -X POST http://127.0.0.1:8081/api/v1/models/load \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "gemma4-e4b",
    "n_ctx": 4096
  }'
```

---

## 📊 모델 벤치마크 (Benchmarking)

### 1. 원스톱 자동 다운로드 + 실측 GPU 벤치마크 (권장)
로컬에 모델 파일이 없는 경우 자동으로 다운로드 후 순차적으로 GPU VRAM에 로드하여 실측 추론 및 품질 평가를 수행합니다.

```bash
uv run python scripts/benchmark_quality.py --auto-download --real
```

### 2. 라이브 서버 추론 벤치마크
현재 실행 중인 서버(`http://127.0.0.1:8081`)를 대상으로 실측 추론 벤치마크를 수행합니다.

```bash
uv run python scripts/benchmark_quality.py --real
```

### 3. 컨텍스트 스케일링 벤치마크
컨텍스트 크기 확장 시 VRAM 점유량 및 지연시간 스케일링을 모니터링합니다.

```bash
uv run python src/scripts/benchmark_context_scaling.py
```

> 벤치마크 종합 분석 결과는 [specs/008-response-quality-eval/analysis_report_quality.md](file:///home/dev/storage/vllm_serv/specs/008-response-quality-eval/analysis_report_quality.md) 경로에 자동 저장됩니다.

---

## 🧪 테스트 실행 (Test Suite)

전체 단위 테스트 및 통합 테스트 수트를 실행합니다 (70+ test cases, 100% Pass).

```bash
# 전체 테스트 실행
uv run pytest tests/ -v

# GPU Detector 및 VRAM 오프로드 검증 테스트만 실행
uv run pytest tests/unit/test_gpu_detector.py tests/integration/test_gpu_validation.py -v
```

---

## 📁 프로젝트 구조 (Project Structure)

```text
vllm_serv/
├── src/
│   ├── core/
│   │   ├── gpu_detector.py         # GPU/CUDA 사전 검증기 및 예외 정의
│   │   ├── process_manager.py      # VRAM 100% 오프로드 파싱 & 서빙 프로세스 수명주기 관리
│   │   ├── llama_manager.py        # 서빙 코디네이터 & VRAM 오프로드 상태 동기화
│   │   ├── model_downloader.py     # HuggingFace Hub 가중치 자동 다운로드 매니저
│   │   ├── event_broadcaster.py    # Asynchronous SSE 브로드캐스터
│   │   └── config_manager.py       # 시스템 설정 관리자
│   ├── eval/
│   │   ├── quality_evaluator.py    # 한국어 구조화 응답 품질 평가기
│   │   └── golden_dataset.json     # Ground Truth 데이터셋
│   └── api/
│       └── server.py               # FastAPI 서빙 엔드포인트
├── scripts/
│   ├── benchmark_quality.py        # 3D 품질-속도-VRAM 교차 벤치마크 러너
│   └── benchmark_qwen35.py         # Qwen 3.5 전용 벤치마크
├── tests/
│   ├── unit/
│   │   ├── test_gpu_detector.py    # GPU 검증기 및 VRAM 오프로드 단위 테스트
│   │   └── test_model_downloader.py# 다운로더 단위 테스트
│   └── integration/
│       ├── test_gpu_validation.py  # CPU 차단 및 VRAM 해제 통합 테스트
│       └── test_quality_benchmark.py# 벤치마크 통합 테스트
├── specs/                          # 기능 명세, 계획 및 벤치마크 보고서
├── pyproject.toml                  # 프로젝트 의존성 및 pytest 설정
└── README.md                       # 본 문서
```

---

## 📜 라이선스 (License)

Apache 2.0 License
