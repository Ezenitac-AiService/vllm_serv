# Data Model & Schema: setup.sh 강제 빌드 및 benchmark_context_window 호환성 스키마

**Feature**: `specs/114-fix-setup-force-build-and-benchmark-crash`  
**Date**: 2026-08-08  

## Entities & Data Structures

### 1. SetupOptions Schema (CLI Arguments in setup.sh)

`scripts/setup.sh` 구동 시 명령줄 인자를 제어하는 옵션 상태 구조입니다.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `WHEEL_PATH` | `string` | `""` | 강제 재설치할 사용자 지정 휠 패키지 경로 (`--wheel-path`) |
| `SKIP_BUILD` | `integer (0/1)` | `0` | 빌드/설치 단계 스킵 플래그 (`--skip-build`) |
| `SKIP_BENCHMARK` | `integer (0/1)` | `0` | 벤치마크 단계 스킵 플래그 (`--skip-benchmark`) |
| `FORCE_BENCHMARK` | `integer (0/1)` | `0` | 벤치마크 강제 재측정 플래그 (`--force-benchmark`) |
| `FORCE_BUILD` | `integer (0/1)` | `0` | **[신규]** Fast-Track 무효화 및 C++ 소스 재컴파일 강제 플래그 (`--force-build`) |

---

### 2. BenchmarkContextState Schema (Context Window Benchmark State)

`scripts/benchmark_context_window.py` 내 `benchmark_context_window()` 실행 시 동적 계산되는 VRAM 및 예산 상태 모델입니다.

| Attribute | Type | Unit | Formula / Description |
|-----------|------|------|-----------------------|
| `total_vram` | `integer` | MB | NVML 또는 OS 물리 GPU 탐지 결과 (기본값: `8192`) |
| `base_vram` | `integer` | MB | 모델 GGUF 가중치 기본 요구량 (`_safe_calculate_base_vram_mb`) |
| `usable_vram` | `integer` | MB | `max(0, total_vram - 1024)` |
| `remaining_kv_budget` | `integer` | MB | `max(0, usable_vram - base_vram)` (n_ctx 할당용) |
| `rec_ctx` | `integer` | Token | `calculate_max_allocatable_n_ctx(usable_kv_budget_mb=remaining_kv_budget, ...)` |
