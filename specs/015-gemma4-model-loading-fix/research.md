# Research & Technical Decisions: Gemma 4 Model Loading Fix & MMProj Vision Projector Binding

**Feature Branch**: `specs/015-gemma4-model-loading-fix`
**Created**: 2026-07-29

---

## Technical Context & Decisions

### Decision 1: Gemma 4 MMProj (CLIP Vision Projector) Mandatory Binding

- **Decision**: `ProcessManager`에서 Gemma 4 계열 모델(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`) 서빙 스폰 시, 프리셋 카탈로그에 지정된 MMProj 파일 경로(`--mmproj` 또는 `--clip_model_path`)를 필수 검증하고 CLI 매개변수로 결합한다.
- **Rationale**:
  - `gemma4` GGUF V3 아키텍처는 `per_layer_token_embd.weight`, `per_layer_model_proj.weight` 등 멀티모달 텐서 맵을 내장하고 있음.
  - `llama-server` / `llama_cpp.server` 구동 시 MMProj 프로젝터를 생략하면 `llama.cpp` CUDA 백엔드가 그래픽 그래프 할당을 중단하고 `offloaded 0/36 layers to GPU`로 폴백됨.
  - MMProj 파일(`gemma-4-E2B-it-mmproj.gguf` 등)을 바인딩하면 `offloaded 36/36 layers to GPU` (100% CUDA VRAM offload)로 동작함.
- **Alternatives Considered**:
  - *Pure-Text Bypass (시도 및 기각)*: 텍스트 전용 서빙을 위해 MMProj를 생략하려 했으나 `llama.cpp` 엔진 한계상 GPU 레이어 오프로드가 0%로 추락하여 헬스체크 타임아웃 발생.

---

### Decision 2: ModelDownloader 원스톱 MMProj 자동 다운로드

- **Decision**: `ModelDownloader.download_model()` 실행 시 카탈로그 프리셋에 `clip` 프로젝터 경로가 정의된 경우, 메인 GGUF 파일과 함께 MMProj 프로젝터 파일도 한 번에 자동 다운로드한다.
- **Rationale**:
  - 사용자가 `gemma4-e2b` 다운로드 시 프로젝터 누락으로 인한 런타임 VRAM 오프로드 에러 발생을 사전 원천 차단함.

---

### Decision 3: 단일 순차 인퍼런스 큐 (`n_seq_max=1`) 정책

- **Decision**: HTTP API 수신은 `asyncio` 비동기 I/O를 유지하되, `llama-server` 인퍼런스 엔진 세션 파라미터는 `n_seq_max=1` / 동시 요청 순차 큐 방식을 유지한다.
- **Rationale**:
  - GTX 1080 Ti (11GB VRAM) 환경에서 병렬 컨텍스트 텐서 할당 시 발생하는 CUDA OOM을 방지하고 예측 가능한 VRAM 점유율(약 1.34 GB ~ 3.2 GB)을 유지함.

---

## Summary of Technical Specifications

| Parameter | Value / Policy |
|-----------|----------------|
| **Python Version** | Python 3.11 (`uv` managed) |
| **LLM Engine** | `llama-server` (compiled CUDA build) with `llama_cpp.server` fallback |
| **CLI Flags (Standalone)** | `llama-server -m <gguf> --mmproj <mmproj_gguf> -c 2048 --port <port> -ngl 999 --split-mode none --main-gpu 0` |
| **CLI Flags (Python Module)** | `python -m llama_cpp.server --model <gguf> --clip_model_path <mmproj_gguf> --n_ctx 2048 --port <port> --n_gpu_layers -1` |
| **VRAM Offload Standard** | 100% layer offload required (`36/36 layers offloaded to GPU`) |
