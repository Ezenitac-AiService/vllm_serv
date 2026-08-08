# Research: 벤치마크 품질 평가 스크립트 VRAM 용량 사전 검증 및 자동 스킵 (Benchmark VRAM Pre-check & Auto-Skip)

**Feature Branch**: `112-benchmark-vram-precheck` | **Date**: 2026-08-08

---

## Technical Decisions & Rationale

### 1. VRAM 요구량 추정 공식 및 모듈 재사용 방식

- **Decision**: `src/core/process_manager.py`에 구현된 `estimate_vram_requirement(file_size_bytes, n_ctx=4096)` 공식 및 `src/core/gpu_detector.py`의 `get_gpu_memory()`를 공통 유틸리티 모듈로 연동.
- **Rationale**:
  - `ProcessManager`는 이미 GGUF 가중치 용량과 Context Window 4K 기준 KV Cache 텐서 VRAM 할당량을 정확히 계산합니다.
  - 다운로더와 벤치마크 스크립트에서 동일한 공식을 사용함으로써 산출 결과의 불일치(Drift)를 완전히 방지합니다.
- **Alternatives Considered**:
  - 파라미터 수(26B/27B) 기반의 하드코딩된 대략적 규칙: GGUF 양자화 레벨(Q4_K_M vs Q8_0)에 따라 실제 파일 용량이 크게 달라지므로 정확도가 떨어짐.

---

### 2. 원격 다운로드 전 VRAM 호환성 검사 시점

- **Decision**: `scripts/model_downloader.py`에서 HuggingFace Hub API 수신 후 실제 파일 차원 다운로드(`hf_hub_download` / `requests`)를 개시하기 직전 `check_vram_feasibility(model_id)` 검사를 실행.
- **Rationale**:
  - 메타데이터 조회(원격 파일 크기 또는 카탈로그 명시 용량)는 수 밀리초 내에 수행되므로, 10GB~17GB의 거대한 파일 다운로드를 시작하기 전에 손쉽게 100% 예측 가능.
- **Alternatives Considered**:
  - 다운로드 중간 체크포인트 스킵: 이미 수 GB 다운로드 후 중단하게 되므로 대역폭 절약 효과가 감퇴함.

---

### 3. 로컬 파일 및 벤치마크 서빙 개설 사전 스킵 연동 (FR-006)

- **Decision**: `scripts/benchmark_quality.py`는 `model_downloader.py` 호환성 검사뿐만 아니라, 이미 `/home/dev/vllm_serv/models/` 디렉터리에 존재하는 가중치 파일로 서빙을 개설하기 전에도 동일한 VRAM 검사를 수행.
- **Rationale**:
  - 로컬에 가중치 파일이 저장되어 있더라도, physical GPU VRAM(예: 11GB)을 초과하면 `llama-server`가 결국 CUDA OOM으로 붕괴하므로, 불필요한 서버 개설 시도 및 런타임 크래시를 전면 차단해야 함.
- **Alternatives Considered**:
  - 로컬 파일은 무조건 프로세스 개설 시도: 런타임 CUDA OOM 크래시가 발생하여 후속 모델 평가에 영향을 미침.

---

### 4. CLI 우회 플래그 (`--ignore-vram-check`) 처리

- **Decision**: `benchmark_quality.py` 및 `model_downloader.py` 공통으로 `--ignore-vram-check` 플래그를 추가하고, 해당 플래그 활성화 시 VRAM 경고 로그만 출력하되 다운로드 및 서빙 개설을 강제 허용.
- **Rationale**:
  - System RAM 수와오프로드 모드나 개발자 오버라이드 테스트 시 유연성을 제공함.
