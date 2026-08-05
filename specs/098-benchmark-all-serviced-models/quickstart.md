# Quickstart & Runnable Validation Guide: 서비스 대상 전체 LLM 모델 기반 컨텍스트 윈도우 스케일링 벤치마크 확장

**Feature**: `098-benchmark-all-serviced-models`
**Created**: 2026-08-05

본 가이드는 본 기능(`098-benchmark-all-serviced-models`)의 구현 완료 후, 수렴 검증(Converge) 및 수동/자동 엔드투엔드 실측 검증을 수행하기 위한 실행 가능 가이드입니다.

---

## Prerequisites (사전 준비 사항)

1. NVIDIA GPU 드라이버 및 CUDA Toolkit (`nvcc`, `nvidia-smi`) 정상 가동 환경.
2. 파이썬 가상환경 동기화 완료:
   ```bash
   uv sync
   ```

---

## Runnable Validation Scenarios (검증 시나리오)

### 시나리오 1: 전체 후보 LLM 모델 대상 강제 실측 벤치마크 (`./setup.sh --force-benchmark`)

**목적**: `--force-benchmark` 플래그로 setup.sh 구동 시 카탈로그 내 모든 LLM 모델에 대해 실제 GPU 프로세스를 스폰하여 벤치마크가 완수되는지 검증합니다.

```bash
# 1. 기존 서버 프로세스 정돈
./stop_server.sh

# 2. 강제 벤치마크 원스톱 셋업 실행
./setup.sh --force-benchmark

# 3. 결과 프로필 JSON 정합성 단정 검증
uv run python -c "
import json
with open('config/model_context_profiles.json', 'r') as f:
    data = json.load(f)
profiles = data.get('profiles', {})
print(f'✅ 수록된 프로파일 수: {len(profiles)}')
assert len(profiles) >= 6, f'Expected at least 6 profiles, got {len(profiles)}'
for m, p in profiles.items():
    print(f'  - [{m}] ctx={p.get(\"recommended_context_length\")}, supported={p.get(\"is_supported\")}, scaling_tested={p.get(\"scaling_tested\")}')
print('🎉 시나리오 1 통과!')
"
```

---

### 시나리오 2: 캐시 고속 스킵 재사용 검증 (`./setup.sh`)

**목적**: 완전 캐시 정합 상태에서 `--force-benchmark` 미부여 시 5초 이내에 실측 벤치마크를 스킵하고 기존 설정을 보존하는지 검증합니다.

```bash
# 1. 스킵 실행 및 시간 측정
START_TIME=$(date +%s)
./setup.sh
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "⏱️ setup.sh 소요 시간: ${ELAPSED}초"
uv run python -c "
assert $ELAPSED <= 10, f'Setup took too long: {$ELAPSED}s'
print('🎉 시나리오 2 고속 스킵 통과!')
"
```

---

### 시나리오 3: 부분 캐시 미스 (Partial Cache Miss) 핀포인트 벤치마크 검증

**목적**: `model_context_profiles.json`에서 특정 모델 키를 삭제한 후 일반 `./setup.sh` 실행 시 누락된 신규 모델만 선택 벤치마크하는지 검증합니다.

```bash
# 1. 임시 테스트용으로 1개 모델 프로필 제거
uv run python -c "
import json
with open('config/model_context_profiles.json', 'r') as f:
    data = json.load(f)
if 'qwen3.5-2b' in data['profiles']:
    del data['profiles']['qwen3.5-2b']
with open('config/model_context_profiles.json', 'w') as f:
    json.dump(data, f, indent=2)
print('🔪 [qwen3.5-2b] 프로파일 임시 삭제 완료')
"

# 2. setup.sh 구동 (핀포인트 동기화 가동)
./setup.sh

# 3. 삭제되었던 모델만 핀포인트 벤치마크로 복구되었는지 검증
uv run python -c "
import json
with open('config/model_context_profiles.json', 'r') as f:
    data = json.load(f)
assert 'qwen3.5-2b' in data['profiles'], '[qwen3.5-2b] 핀포인트 복구 실패!'
print('🎉 시나리오 3 핀포인트 캐시 동기화 통과!')
"
```

---

### 시나리오 4: 타임아웃 및 OOM 비파괴적 폴백 검증 (`is_supported=False`)

**목적**: 하드웨어 리소스 초과 또는 스폰 실패 시 해당 모델이 `is_supported=False`로 마킹되고 exit 0으로 파이프라인이 완료되는지 검증합니다.

```bash
uv run python -c "
from scripts.benchmark_context_window import run_fine_grained_binary_search
# 존재하지 않거나 과도한 가상 모델 스폰 테스트
res = run_fine_grained_binary_search(model_name='non-existent-overlarge-model')
assert res is not None
print('🎉 시나리오 4 비파괴적 폴백 통과!')
"
```

---

### 시나리오 5: 전체 회귀 테스트 수트 실행 (Full Suite Regression)

**헌법 VII조(Mandatory Regression Testing Rule)**에 따라 구현 후 전체 pytest 회귀 수트를 실행합니다.

```bash
uv run pytest
```
