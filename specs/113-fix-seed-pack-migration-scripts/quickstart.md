# Quickstart Validation Guide: 시드 팩 마이그레이션 파이프라인 및 ProcessManager 호환성 전수 검증 (Fix Seed Pack Migration Pipeline & ProcessManager Compatibility)

## 1. 개요 (Overview)

본 가이드는 타 서버 및 다른 플랫폼으로 이관할 때 `make_seed_pack.sh` 생성 -> `unpack_seed.sh` 복원 -> `./setup.sh` 환경 구성 -> 벤치마크 스크립트 실행 전체 파이프라인이 `AttributeError`나 파일 누락 없이 100% 정상 작동하는지 실측 검증하는 시나리오를 제공합니다.

---

## 2. 사전 조건 (Prerequisites)

- `uv` 패키지 매니저 설치 (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Bash 쉘 환경 및 standard tar/zip 유틸리티

---

## 3. 실측 검증 시나리오 (Validation Steps)

### Step 1: ProcessManager 인스턴스 및 정적 메서드 호환성 검증

```bash
uv run python -c "
from src.core.process_manager import ProcessManager

# 1. Static call test
print('Static calculate_base_vram_mb:', ProcessManager.calculate_base_vram_mb('', None))

# 2. Instance call test
pm = ProcessManager()
print('Instance calculate_base_vram_mb:', pm.calculate_base_vram_mb('', None))
print('Has force_kill_zombie_llama_servers on class:', hasattr(ProcessManager, 'force_kill_zombie_llama_servers'))
print('Has force_kill_zombie_llama_servers on instance:', hasattr(pm, 'force_kill_zombie_llama_servers'))
"
```

**기대 결과**:
- Static 및 Instance 양쪽 호출 모두에서 `AttributeError` 없이 `6000` 기본값 반환 및 `True` 출력.

---

### Step 2: 시드 팩 아카이브 생성 및 전수 무결성 수록 검증 (`make_seed_pack.sh`)

```bash
./scripts/make_seed_pack.sh -o dist/vllm_serv_seed_test.tar.gz
```

**기대 결과**:
- `process_manager.py`, `model_downloader.py`, `benchmark_quality.py`, `benchmark_context_window.py`, `setup.sh`, `unpack_seed.sh`, `make_seed_pack.sh` 등 100% 필수 스크립트가 수록되었음이 `[SEED-PACK INFO] ✓ ... 아카이브 수록 검증 완료`로 표시됨.

---

### Step 3: 압축 해제 및 사전/사후 검증 (`unpack_seed.sh`)

```bash
mkdir -p /tmp/vllm_serv_test_unpack
./scripts/unpack_seed.sh -i dist/vllm_serv_seed_test.tar.gz -t /tmp/vllm_serv_test_unpack -f
```

**기대 결과**:
- `✓ [PRE-UNPACK PASS] 필수 구성 파일 전수 수록 검증 성공` 및 사후 검증 `✓ Seed Pack 안전 압축 해제 완결!` 출력.

---

### Step 4: setup.sh 필수 검증 및 벤치마크 드라이런 검증

```bash
./setup.sh --skip-build --skip-benchmark
uv run python scripts/benchmark_context_window.py --skip-benchmark
```

**기대 결과**:
- `Step 1. 필수 프로젝트 기본 파일 존재 여부 검증` 통과 및 `benchmark_context_window.py` 구동 시 `AttributeError` 0건 발생.

---

### Step 5: 전체 단위 회귀 테스트 수트 실행

```bash
uv run pytest tests/unit/
```

**기대 결과**:
- 100% 테스트 PASS.
