# Quickstart: Validation & Verification Guide (041-uv-sync-performance-fix)

Feature `041-uv-sync-performance-fix` 속도 최적화 검증을 위한 실측 실행 명령어 및 가이드입니다.

---

## 1. setup.sh `uv sync` 실행 시간 2초 이내 단축 실측

```bash
# setup.sh 실행 시간 측정
time ./scripts/setup.sh

# Expected Result:
# Step 2 로그: "[SETUP INFO] 가상환경 고속 동기화 중 (uv sync --frozen)..."
# Step 2 소요 시간 < 2초
```

---

## 2. 오프라인 / 락파일 미존재 Fallback 검증

```bash
# uv.lock이 없는 상태에서도 자동 Fallback으로 정상 완납되는지 검증
uv run pytest tests/unit/test_shell_scripts.py -k test_setup_uv_sync_performance -v
```
