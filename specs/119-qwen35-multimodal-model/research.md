# Phase 0 Research: Qwen 3.5 9B 멀티모달 모델 검증 및 카탈로그 등록

## 1. 모델 조사 및 가중치 사양 (Model Specifications)

- **Hugging Face Repository**: `unsloth/Qwen3.5-9B-GGUF`
- **Main Model GGUF**: `Qwen3.5-9B-Q4_K_M.gguf` (약 5.8 GB)
- **Vision Projector (mmproj)**: `mmproj-BF16.gguf` (BF16 정밀도 비전 투영기)
- **Quantization Type**: `q4_k_m`
- **Chat Template**: `chatml`
- **Estimated VRAM**: `9800 MB`
- **Context Length**: default `4096`, max `131072`

### Decision:
기존 `qwen3.5-9b` 항목은 텍스트 전용(`requires_mmproj: false`)으로 유지하고, 신규 멀티모달 항목으로 `qwen3.5-9b-vision` 키를 카탈로그(`config/model_catalog.json`)에 추가한다.

### Rationale:
1. 기존 운영 중인 라우팅 및 서비스 API의 깨짐(Breaking Changes)을 원천 방지한다.
2. `gemma4-e2b`(비전)과 `gemma4-2b-text`(텍스트 전용)처럼 일관된 프로젝트 규칙을 유지한다.
3. 비전 프로젝터로 `mmproj-BF16.gguf`를 설정하여 `llama-server` 엔진의 멀티모달 인퍼런스를 원활히 지원한다.

### Alternatives Considered:
- **기존 `qwen3.5-9b` 항목을 `requires_mmproj: true`로 직접 수정**: 기존 텍스트 전용 호출 프로세스나 더 적은 VRAM을 기대하는 클라이언트 서비스에 장애를 일으킬 위험이 있어 기각함.
- **`qwen3.5-9b-multimodal` 식별자 채택**: 식별자 길이가 길고 기존 프로젝트 컨벤션(`vision`, `text`)과 다소 괴리가 있어 기각함.

---

## 2. 시스템 구성 요소 및 연동 분석 (System Integration)

1. **`config/model_catalog.json`**:
   - `qwen3.5-9b-vision` 신규 엔트리 추가.
   - `target_dir`: `models/qwen3.5-9b-vision`
   - `model_path`: `models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf`
   - `clip_path`: `models/qwen3.5-9b-vision/mmproj-BF16.gguf`
   - `requires_mmproj`: `true`

2. **`scripts/ensure_models.py` & `scripts/start_server.sh`**:
   - `requires_mmproj: true`인 모델 파싱 시 `clip_filename` 및 `clip_path` 파일 존재 여부 검증.
   - `start_server.sh` 구동 시 `requires_mmproj` 조건 충족 시 `llama-server` 인자에 `--mmproj <clip_path>` 자동 추가 연동 확인.

3. **테스트 검증 수트**:
   - `tests/unit/test_model_catalog.py` (또는 관련 카탈로그 무결성 테스트 수트)에 `qwen3.5-9b-vision` 식별자 검증 케이스 추가.
