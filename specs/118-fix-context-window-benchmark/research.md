# Phase 0 Research: 마이그레이션 RTX 3060 플랫폼 컨텍스트 윈도우 벤치마크 전수 평가 및 동적 KV 캐시 VRAM 오탐 수정

## Decision 1: ProcessManager 내 GQA 아키텍처 파라미터 동적 추출 및 KV 캐시 산출식 연동

- **Decision**: `ProcessManager.spawn_process()` 사전 검사 및 `estimate_vram_usage()` 호출 시, `ConfigManager` 카탈로그 엔트리 또는 `read_gguf_metadata_architecture(model_file)`에서 모델별 `n_layers`, `n_heads`, `n_head_kv`, `head_dim` 파라미터를 동적으로 추출하여 `estimate_kv_cache_vram()`에 인자로 전달한다.
- **Rationale**:
  - 기존에는 `estimate_kv_cache_vram(n_ctx=n_ctx)`를 기본 인자로만 호출하여 하드코딩된 디폴트 파라미터(`n_layers=36`, `n_heads=32`, `head_dim=128`)가 적용되었습니다.
  - 이로 인해 Qwen 3.5 2B/4B, Gemma 4 2B/4B 등 소형/GQA 아키텍처 모델에서도 `n_ctx=16384`일 때 9,216MB KV 캐시가 오탐 산출되어 `Estimated VRAM 15,216MB`로 억울하게 프로세스 스폰이 차단되었습니다.
  - 모델 카탈로그 및 GGUF 헤더 파라미터(예: Qwen 3.5 2B: `n_layers=24`, `n_heads=16`, `n_head_kv=8`)를 전달받아 계산하면 `n_ctx=16384`에서도 약 1,536MB~2,048MB 내외의 실제 KV 캐시 용량이 정밀 계산되어 16K 스케일링 측정이 정상 스폰됩니다.
- **Alternatives Considered**:
  - 단순 오버헤드 마진 상한선 확대 (`vram_max_capacity_mb + 5000` 등): 임시 차단은 회피할 수 있으나 실제 VRAM 계산 오탐 문제가 근본적으로 해결되지 않으므로 기각.

---

## Decision 2: benchmark_context_window.py CLI --all 전수 카탈로그 평가 모드 추가

- **Decision**: `scripts/benchmark_context_window.py` CLI 인자에 `--all` 옵션을 신규 추가하고, `--all` 지정 시 `get_candidate_llm_models()`에 정의된 모든 LLM 모델(Qwen, Gemma 라인업)을 순차적으로 이진 탐색 평가하여 `config/model_context_profiles.json` 프로파일을 전수 반영하도록 확장한다.
- **Rationale**:
  - 현재 CLI는 `--model qwen3.5-4b` 디폴트로 동작하여 인자를 전달하지 않으면 단 1개 모델만 평가하고 종료되는 문제가 있었습니다.
  - `--all` 플래그를 추가하면 단 한 번의 CLI 실행으로 3060 플랫폼 상의 모든 가용 모델의 최적 컨텍스트 윈도우 프로파일을 자동 완성할 수 있습니다.
- **Alternatives Considered**:
  - `--force-benchmark` 옵션 재활용: 기존 `--force-benchmark`는 4단계 C-B-A 모듈화 벤치마크용이므로, 독립적인 이진 탐색 평가를 위한 `--all` 플래그를 명시적으로 분리 수록함.

---

## Decision 3: benchmark_quality.py [Step 5.1] 동적 VRAM Pre-flight 체크 정밀화

- **Decision**: `scripts/benchmark_quality.py`의 [Step 5.1] 컨텍스트 스케일링 루프 실행 시 `pm.estimate_vram_usage(model_id, target_n_ctx)`를 통해 정밀 계산된 VRAM 사용량을 참조하여 16K 스케일링 구간에서 오탐 차단 없이 실제 측정이 수행되도록 개선한다.
- **Rationale**:
  - 종합 품질 벤치마크 리포트(`analysis_report_quality.md`) 생성 시 모델별 실제 가능한 컨텍스트 스케일링 성능 데이터(2K, 4K, 8K, 16K)가 100% 정밀하게 기록되도록 보장합니다.
