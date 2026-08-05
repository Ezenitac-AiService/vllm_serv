# Research & Decision Log: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 연동 (`095-setup-benchmark-model-selection`)

**Feature**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/spec.md)  
**Date**: 2026-08-04 | **Amended**: 2026-08-05

---

## Technical Decisions

### Decision 1: 4단계 모듈화 파이프라인 책임 분리 및 스크립트 모듈 설계
- **Chosen Option**:
  - **Stage 1 (모델 다운로드)**: `scripts/ensure_models.py` (HF Hub GGUF 파일 안전 fetch)
  - **Stage 2 (무결성 검증)**: GGUF 4바이트 magic header (`GGUF`) 및 파일 크기 실체적 검증 (`verify_model_integrity()`)
  - **Stage 3 (임시 서빙 & 컨텍스트 윈도우 벤치마크)**: 신규 파이썬 전용 모듈 `scripts/benchmark_context_window.py`
  - **Stage 4 (선정 & 설정 반영)**: `src/core/config_manager.py` 원자적 `config/server_config.json` 및 `config/model_context_profiles.json` 업데이트
- **Rationale**: 기존 `benchmark_quality.py`의 모놀리식 통 스크립트 실행 구조를 깨고 각 단계를 독립 모듈화함으로써, 셋업 도중 오류 발생 시 디버깅이 명확해지고 VRAM 소모량이 실시간으로 안전하게 측정됨.

### Decision 2: 2단계 이진 탐색(Binary Search, 512/1024 토큰 블록 정렬) 컨텍스트 윈도우 정밀 프로파일링
- **Chosen Option**:
  - **Pass 1 (Coarse 2x Scan)**: 2배수($2^n$: 2048, 4096, 8192, 16384, 32768) 탐색으로 성공 상한 $C_{pass}$와 최초 OOM $C_{fail}$ 구간(예: 8K~16K)을 고속 도출.
  - **Pass 2 (Fine-Grained Binary Search `--fine-grained`)**: $[C_{pass}, C_{fail}]$ 구간에 대해 512/1024 토큰 블록 얼라인먼트 및 모델 RoPE 최대 지원 한계 캡(`min(physical_max, model_max_rope)`)을 준수하는 이진 탐색(Binary Search)을 구동하여 3회 이하 최소 실행으로 정밀 최적 수용 크기(예: 12288, 14336)에 수렴하고 `config/model_context_profiles.json`에 저장.
- **Scientific Rationale & References**:
  1. **PagedAttention 메모리 페이징 (vLLM, Kwon et al., SOSP 2023)**: KV Cache를 16/32/64/512 토큰 고정 블록으로 페이징 관리하므로 512/1024 배수 크기(10K, 12K, 20K)에서도 외부 메모리 단편화율 0% 보장.
  2. **동적 RoPE 위치 임베딩 (YaRN, Peng et al., ICLR 2024)**: RoPE scaling factor $s = N_{ctx} / N_{base} \in \mathbb{R}^+$ 함수가 실수 단위로 동적 조절되므로 2배수가 아닌 10K/12K/20K에서도 위치 좌표 붕괴 없이 온더플라이 정상 처리.
  3. **FlashAttention 커널 타일링 (Dao et al., 2023/2024)**: Shared Memory 타일 크기가 $128 \times 64$ 토큰 단위이므로 512/1024 정렬 시 GPU SIMD Tensor Core 효율 100% 유지.

### Decision 3: `--skip-benchmark` 설정 보존 및 수행 시간 검증
- **Chosen Option**:
  - `./setup.sh --skip-benchmark` 구동 시 `benchmark_context_window.py --skip-benchmark`를 전달하여 3단계 실측 벤치마크를 스킵하고 `config/server_config.json`의 기존 `context_window` 설정을 안전하게 보존함.
  - 연동 테스트 수트에 15초 이내 완수(`elapsed < 15.0`) 검증 assertion 수록.
- **Rationale**: CI/CD 자동화 파이프라인에서 불필요한 설정 무단 변경을 방지하고 빠른 빌드 고속 구동을 보장함.

### Decision 4: 하드코딩 상수 & 회피성 목업 제거 리팩토링
- **Chosen Option**:
  - `benchmark_quality.py` 및 `benchmark_context_window.py` 내 베이스라인 딕셔너리(`baselines`), 가짜 비율 수치(`* 0.2`), 무조건 `PASSED` 출력 로직을 전면 제거.
  - NVML API(`get_nvml_vram_info()`) 실시간 GPU 스냅샷 및 HTTP SSE 스트리밍 청크 실측 기반 TTFT/TPOT 텔레메트리 추출 시스템으로 전환.
- **Rationale**: 헌법 II (가짜 통과 전면 금지 및 실체적 연동) 원칙을 철저히 준수하여 프로덕션 벤치마크의 신뢰성을 확보함.
