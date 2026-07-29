# Phase 0 Research: 자동 모델 다운로드 및 동적 서빙 프로세스 실행 관리 (Automatic Model Download & Dynamic Serving Automation)

**Feature Branch**: `009-auto-model-download-serving`
**Date**: 2026-07-29

## Executive Summary & Research Objectives

본 연구는 `Qwen 3.5` (2B/4B/9B) 및 `Gemma 4` (E2B/E4B/12B) GGUF 가중치 모델 파일의 **HuggingFace Hub 자동 다운로드**, **GPU VRAM 동적 해제 및 llama-server 서빙 프로세스 무중단 스위칭**, 그리고 **실제 GPU Cuda 코어 및 VRAM 실측 원스톱 벤치마크 파이프라인**을 구축하기 위해 진행되었습니다.

---

## 1. HuggingFace Hub GGUF 자동 다운로드 체계

### Decision
`huggingface_hub` 라이브러리의 `hf_hub_download` API를 활용하여 `Qwen/Qwen3.5-GGUF` 및 `google/gemma-4-GGUF` 리포지토리로부터 필요한 정밀도별 GGUF 파일 및 CLIP 프로젝터(`mmproj`)를 `models/<model_id>/` 디렉토리에 자동 다운로드합니다.

- **Qwen 3.5 2B**: `Qwen/Qwen3.5-2B-Instruct-GGUF` -> `qwen-3.5-2b-instruct-q4_k_m.gguf`
- **Qwen 3.5 4B**: `Qwen/Qwen3.5-4B-Instruct-GGUF` -> `qwen-3.5-4b-instruct-q4_k_m.gguf`
- **Qwen 3.5 9B**: `Qwen/Qwen3.5-9B-Instruct-GGUF` -> `qwen-3.5-9b-instruct-q4_k_m.gguf`
- **Gemma 4 E2B**: `lmstudio-community/gemma-4-E2B-it-GGUF` -> `gemma-4-E2B_q4_0-it.gguf` & `mmproj`
- **Gemma 4 E4B**: `lmstudio-community/gemma-4-E4B-it-GGUF` -> `gemma-4-E4B_q4_0-it.gguf` & `mmproj`
- **Gemma 4 12B**: `lmstudio-community/gemma-4-12b-it-GGUF` -> `gemma-4-12b-it-qat-q4_0.gguf` & `mmproj`

### Rationale
수동 다운로드 절차 없이 코드가 실행될 때 미존재 가중치를 자동 감지하여 이어받기(Resume) 모드로 안정적으로 확보합니다.

---

## 2. 동적 프로세스 스위칭 및 GPU VRAM 완전 해제 메커니즘

### Decision
`src/core/process_manager.py`를 확장하여 모델 전환 시 이전 `llama-server` 프로세스에 대해 `SIGTERM` ➔ 5초 타임아웃 ➔ `SIGKILL` 에스컬레이션을 적용하고, OS 프로세스 포트(`8081`) 소켓이 클리어되었음을 확인한 후 신규 모델 프로세스를 개설합니다.

- `HTTP GET http://127.0.0.1:8081/v1/models`로 서빙 헬스체크 수행 (최대 30초 대기)
- `READY` 상태가 확인된 후 HTTP 요청 전송

---

## 3. 풀 원스톱 실측 벤치마크 자동화 (`scripts/benchmark_quality.py`)

### Decision
`scripts/benchmark_quality.py`에 `--auto-download` 및 `--real-inference` 옵션을 수록하여, 6개 모델에 대해 [다운로드 ➔ 서버 개설 ➔ 실측 추론 ➔ VRAM 반납] 전 과정을 자동 루프로 실행하도록 구현합니다.
