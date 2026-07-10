# Data Model: llama.cpp 양자화 모델 서비스

## Entities

### ModelConfig
- **description**: 벤치마크 및 런타임 로드를 위한 모델 설정 정보
- **fields**:
  - `model_id` (string): 예 - "gemma4-12b", "gemma4-4b"
  - `repo_id` (string): HuggingFace 저장소 ID
  - `filename` (string): GGUF 파일명
  - `n_ctx` (int): 4096 (고정)

### BenchmarkResult
- **description**: 벤치마크 스크립트의 모델별 측정 결과
- **fields**:
  - `model_id` (string)
  - `load_time_sec` (float): 모델 로딩 시간
  - `vram_used_mb` (float): 로드 직후 VRAM 사용량
  - `tpot_ms` (float): 토큰당 생성 시간 (Time Per Output Token)
  - `status` (string): "SUCCESS" or "OOM"
