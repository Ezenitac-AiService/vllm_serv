# Quickstart & Runnable Validation Scenarios: setup.sh 폴리싱 및 GPU 모델 로드 실측 벤치마크 파이프라인 리팩토링 (099-fix-setup-gpu-benchmark)

## 1. 사전 준비사항 (Prerequisites)

- NVIDIA GPU (GeForce GTX 1080 Ti 이상) 및 CUDA 드라이버 설치
- `uv` 패키지 매니저 및 파이썬 가상환경 설치 (`uv sync`)
- 필수 GGUF 모델 가중치 (`models/` 디렉토리에 `.gguf` 파일 존재)

---

## 2. 검증 시나리오 (Runnable Validation Scenarios)

### Scenario 1: `./setup.sh --force-benchmark` 구동 시 실제 GPU 로딩 및 TPS 실측 검증

**실행 명령어**:
```bash
./setup.sh --force-benchmark
```

**기대 결과**:
1. Step 0/1에서 기존 실행 중인 `llama-server` 프로세스가 감지되어 원자적으로 정돈(Pre-cleanup)됨.
2. Step 2.8 구동 중 별도 터미널에서 `nvtop` 또는 `nvidia-smi` 모니터링 시 각 모델(`gemma4-e2b`, `qwen3.5-4b` 등) 평가 시점마다 GPU VRAM 용량 상승 및 GPU Util 사용률 100% 점유가 실시간으로 관측됨.
3. 벤치마크 완료 후 출력되는 터미널 리포트에 실측 TPS가 `TPS: 45.0` 등 양수로 표시되고 `Supported: True`로 선정됨.
4. Step 4.5 도달 시 "캐시 프로필 완비" 메시지와 함께 5초 이내 고속 스킵(Smart Skip)됨.
5. Step 5 완료 후 `./start_server.sh`가 자동 실행되어 서빙 포트(8081) 헬스체크가 정상 완수됨 (`status: ok`).

---

### Scenario 2: `config/model_context_profiles.json` 원자적 검증 및 스키마 검수

**실행 명령어**:
```bash
uv run pytest tests/unit/test_config_manager_profiles.py -v
```

**기대 결과**:
1. 모든 모델의 실측 프로필 항목에 `is_supported=true`, `tpot_tok_per_sec > 0.0`, `peak_vram_mb > 0`이 정상 수록되어 있는지 검증 통과 (`PASSED`).

---

### Scenario 3: 비정상 종료 (SIGINT / Ctrl+C) 시 자율 자원 회수 검증

**실행 명령어**:
```bash
uv run python scripts/benchmark_context_window.py --force-benchmark
# 구동 중 Ctrl+C 입력하여 강제 중단
```

**확인 명령어**:
```bash
ps aux | grep llama-server
```

**기대 결과**:
1. Python `signal` 핸들러 및 `atexit` 훅에 의해 백그라운드 `llama-server` 프로세스 및 8081 포트 점유가 100% 소멸되어 검색 결과가 존재하지 않음.

---

### Scenario 4: 전체 회귀 테스트 수트 검증

**실행 명령어**:
```bash
uv run pytest -v
```

**기대 결과**:
1. 전체 회귀 테스트 수트가 파손 없이 100% 통과 (`Green Pass`).
