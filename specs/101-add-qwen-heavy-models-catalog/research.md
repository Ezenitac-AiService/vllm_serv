# Research & Technical Decisions: 101-add-qwen-heavy-models-catalog

## 1. 카탈로그 확장 대상 모델 메타데이터 조사 및 결정 (Model Catalog Expansion Research)

### Decision
`config/model_catalog.json`에 신규 대형 및 텍스트 전용 GGUF 모델 6종을 추가하고, 기존 8개(LLM 6개 + Aux 2개) 항목을 14개(LLM 12개 + Aux 2개)로 확장합니다.

### Technical Metadata Breakdown
1. **`qwen3.6-27b`**:
   - `repo_id`: `unsloth/Qwen3.6-27B-GGUF`
   - `filename`: `Qwen3.6-27B-Instruct-Q4_K_M.gguf`
   - `vram_est_mb`: 19500 (Base VRAM ~19.5GB)
   - `size_gb`: 16.5
   - `quant_type`: `q4_k_m`, `chat_template`: `chatml`, `requires_mmproj`: false
2. **`qwen3.6-35b-a3b`**:
   - `repo_id`: `unsloth/Qwen3.6-35B-A3B-GGUF`
   - `filename`: `Qwen3.6-35B-A3B-Q4_K_M.gguf`
   - `vram_est_mb`: 24500 (Base VRAM ~24.5GB, MoE 35B total / 3B active)
   - `size_gb`: 21.0
   - `quant_type`: `q4_k_m`, `chat_template`: `chatml`, `requires_mmproj`: false
3. **`gemma4-26b-a4b`**:
   - `repo_id`: `unsloth/gemma-4-26B-A4B-it-GGUF`
   - `filename`: `gemma-4-26B-A4B-it-Q4_K_M.gguf`
   - `vram_est_mb`: 18800 (Base VRAM ~18.8GB, MoE 26B total / 4B active)
   - `size_gb`: 15.8
   - `quant_type`: `q4_k_m`, `chat_template`: `gemma`, `requires_mmproj`: false
4. **`gemma4-2b-text`**:
   - `repo_id`: `unsloth/gemma-4-2b-it-GGUF`
   - `filename`: `gemma-4-2b-it-Q4_K_M.gguf`
   - `vram_est_mb`: 2800, `size_gb`: 1.6, `requires_mmproj`: false
5. **`gemma4-4b-text`**:
   - `repo_id`: `unsloth/gemma-4-4b-it-GGUF`
   - `filename`: `gemma-4-4b-it-Q4_K_M.gguf`
   - `vram_est_mb`: 5200, `size_gb`: 2.9, `requires_mmproj`: false
6. **`gemma4-12b-text`**:
   - `repo_id`: `unsloth/gemma-4-12b-it-GGUF`
   - `filename`: `gemma-4-12b-it-Q4_K_M.gguf`
   - `vram_est_mb`: 9200, `size_gb`: 7.2, `requires_mmproj`: false

### Rationale
- `unsloth` 및 `lmstudio-community`는 llama.cpp 및 vLLM / GGUF 호환성이 100% 검증된 표준 Q4_K_M 양자화 파라미터 공급처입니다.
- 시각(mmproj) 비의존성 텍스트 전용 Gemma 4 모델 3종을 추가하여 순수 텍스트 인퍼런스 워크로드 시 VRAM 점유 및 연산 오버헤드를 경량화할 수 있습니다.

---

## 2. 벤치마크 및 setup.sh 파이프라인에서 대형 모델 안전 배제 메커니즘 (Safe Exclusion in Setup Pipeline)

### Decision
- `scripts/benchmark_context_window.py` 내 `get_candidate_llm_models()`는 `config/model_catalog.json`의 모든 LLM 항목(`task_type`이 `embedding` 또는 `rerank`가 아닌 모델 12종)을 동적으로 로드합니다.
- `benchmark_context_window()` 평가 시 pre-flight 자원 점검 단계:
  ```python
  if usable_vram_mb < base_vram_mb:
      # OOM 발생 위험으로 사전 차단 및 is_supported: false 기록
      profile["is_supported"] = False
      profile["failure_reason"] = f"CUDA OOM Risk: Base VRAM ({base_vram_mb}MB) exceeds Usable VRAM ({usable_vram_mb}MB)"
  ```
- 이 메커니즘을 통해 11GB VRAM GTX 1080 Ti 환경에서 18GB~24GB Base VRAM이 필요한 대형 모델 3종(`qwen3.6-27b`, `qwen3.6-35b-a3b`, `gemma4-26b-a4b`)이 안전하게 배제되며, 벤치마크 루프는 예외 던짐 없이 다음 모델 평가로 진행됩니다.

### Rationale
- OOM 발생을 사전에 NVML Usable VRAM 기반으로 차단함으로써 하드웨어를 보호하고, 무거운 20GB 모델의 런타임 OOM 소환 시도를 안전하게 방지합니다.

---

## 3. 대형 모델 배제 후 유효 최적 모델 선정 및 동적 폴백 (Dynamic Serving Selection & Fallback)

### Decision
`benchmark_context_window.py` 완료 시 `is_supported: True`이면서 가장 높은 TPS를 도출한 유효 모델(예: `qwen3.5-4b` 또는 `gemma4-e4b`)이 서빙 모델로 선정되어 `config/server_config.json`의 `active_model` 항목에 자동 기록됩니다.

### Rationale
고용량 대형 모델이 지원 차단되더라도 시스템 전체 서빙 파이프라인은 멈추지 않고 가용한 최대 성능 모델을 자동으로 선택하게 됩니다.
