# Data Model: 자동 모델 다운로드 및 동적 서빙 프로세스 실행 관리 (Automatic Model Download & Dynamic Serving Automation)

**Feature Branch**: `009-auto-model-download-serving`
**Date**: 2026-07-29

## Entities & Schemas

### 1. `ModelDownloadTask` (모델 다운로드 엔티티)

| Field Name | Type | Description |
|------------|------|-------------|
| `model_id` | `str` | 모델 식별자 (예: `"qwen3.5-2b"`, `"gemma4-e2b"`) |
| `repo_id` | `str` | HuggingFace Repository ID (예: `"Qwen/Qwen3.5-2B-Instruct-GGUF"`) |
| `filename` | `str` | GGUF 가중치 파일명 |
| `clip_filename` | `Optional[str]` | CLIP 프로젝터 파일명 (Gemma 4 멀티모달용) |
| `target_dir` | `str` | 로컬 저장 디렉토리 (`"models/qwen3.5-2b/"`) |
| `is_completed` | `bool` | 다운로드 완수 여부 |
| `download_progress_pct` | `float` | 진행률 (`0.0` ~ `100.0`) |

---

### 2. `ServerProcessState` (서빙 프로세스 상태 엔티티)

| Field Name | Type | Description |
|------------|------|-------------|
| `status` | `str` | `"UNLOADED"`, `"DOWNLOADING"`, `"LOADING"`, `"READY"`, `"ERROR"` |
| `model_id` | `Optional[str]` | 로딩된 모델 ID |
| `port` | `int` | 바인딩 포트 (기본 `8081`) |
| `pid` | `Optional[int]` | OS 프로세스 PID |
| `error_message` | `Optional[str]` | 에러 메시지 |
