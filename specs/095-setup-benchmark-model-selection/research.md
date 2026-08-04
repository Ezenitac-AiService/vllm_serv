# Research & Decision Log: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 연동 (`095-setup-benchmark-model-selection`)

**Feature**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/spec.md)  
**Date**: 2026-08-04

---

## Technical Decisions

### Decision 1: 4단계 모듈화 파이프라인 책임 분리 및 스크립트 모듈 설계
- **Chosen Option**:
  - **Stage 1 (모델 다운로드)**: `scripts/ensure_models.py` (HF Hub GGUF 파일 안전 fetch)
  - **Stage 2 (무결성 검증)**: GGUF 헤더 및 파일 바이트 무결성 검증
  - **Stage 3 (임시 서빙 & 컨텍스트 윈도우 벤치마크)**: 신규 파이썬 전용 모듈 `scripts/benchmark_context_window.py`
  - **Stage 4 (선정 & 설정 반영)**: `src/core/config_manager.py` 원자적 `config/server_config.json` 업데이트
- **Rationale**: 기존 `benchmark_quality.py`의 모놀리식 통 스크립트 실행 구조를 깨고 각 단계를 독립 모듈화함으로써, 셋업 도중 오류 발생 시 디버깅이 명확해지고 VRAM 소모량이 실시간으로 안전하게 측정됨.
- **Alternatives Considered**:
  - 통째로 `benchmark_quality.py` 스크립트를 쉘에서 무조건 실행하기 (기존 초기 의존성 유입 및 디버깅 불투명으로 기각).

### Decision 2: 컨텍스트 윈도우 벤치마크 (2K ~ 16K) 실측 VRAM & TPS 한계선 판정 알고리즘
- **Chosen Option**:
  - 후보 서빙 모델(`qwen3.5-4b.gguf` 등)을 `llama-server` 또는 Python C-API 임시 프로세스로 가동 후, 컨텍스트 크기($N \in [2048, 4096, 8192, 16384]$) 단계별 오프셋으로 숏/롱 프롬프트를 전송.
  - 호스트 VRAM 사용량이 전체 VRAM의 90%를 초과하지 않고, TPS(Tokens Per Second)가 최소 기준치(예: 10 tps)를 유지하는 최대 컨텍스트 윈도우 크기를 최적값으로 확정.
- **Rationale**: 물리 GPU VRAM 한계를 넘어서는 컨텍스트 설정은 OOM 크래시를 유발하므로, 실측 벤치마크를 통해 90% Safety Margin을 확보하는 것이 필수적임.

### Decision 3: `--skip-benchmark` 및 비대화형(CI/CD) 안전 폴백
- **Chosen Option**:
  - `./setup.sh --skip-benchmark` 또는 비대화형 환경 실행 시 Stage 3 벤치마크 단계를 안전하게 건너뛰고, `config/server_config.json`의 기존 설정값(또는 하드웨어 프로파일 기본 안전값 `context_window=4096`)을 보존함.
- **Rationale**: CI/CD 자동화 빌드나 테스트 러너에서 매번 벤치마크를 수행하는 시간을 획기적으로 줄이고 고속 셋업을 지원함.
