# Data Model: 벤치마크 VRAM 사전 검증 및 자동 스킵 데이터 구조

**Feature Directory**: `specs/112-benchmark-vram-precheck`

---

## Data Entities

### 1. `VRAMPrecheckResult` (VRAM 사전 검증 결과)

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `model_id` | `str` | 모델 식별자 (예: `gemma4-26b-a4b`, `qwen3.6-27b`) | Non-empty |
| `file_size_bytes` | `int` | GGUF 가중치 파일 크기 (바이트) | >= 0 |
| `estimated_vram_mb` | `float` | 가중치 + KV Cache 추정 VRAM 사용량 (MB) | > 0 |
| `available_vram_mb` | `float` | 물리 GPU 사용 가능한 VRAM 용량 (MB) | >= 0 |
| `is_feasible` | `bool` | VRAM 수용 가능 여부 판정 | True / False |
| `status_code` | `str` | 판정 상태 코드 (`PASS`, `SKIP_OOM_RISK`, `BYPASS_WARNING`) | Enum |
| `message` | `str` | 사용자 안내 메시지 (한국어) | Non-empty |

---

### 2. `BenchmarkVRAMSummary` (벤치마크 전수 검사 요약)

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `gpu_name` | `str` | 감지된 GPU 장치명 (예: `NVIDIA GeForce GTX 1080 Ti`) | Non-empty |
| `total_vram_mb` | `float` | 감지된 물리 VRAM 용량 (MB) | > 0 |
| `total_models` | `int` | 평가 대상 전체 모델 수 | > 0 |
| `passed_count` | `int` | VRAM 검증 통과 모델 수 | >= 0 |
| `skipped_count` | `int` | VRAM 용량 초과 스킵 모델 수 | >= 0 |
| `evaluations` | `List[VRAMPrecheckResult]` | 모델별 사전 검증 결과 객체 목록 | List |
