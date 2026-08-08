# Quickstart & Integration Validation Guide: README.md 검증 가이드

**Feature**: `specs/115-rewrite-readme-documentation`  
**Date**: 2026-08-08  

## Validation Scenarios

### Scenario 1: README.md 내 에이전트/Speckit 관련 용어 상실 검증

```bash
# 1. 실행 명령
grep -iE "speckit|slash command|/speckit-|agents/" README.md || echo "CLEAN"

# 2. 기대 결과
# - 출력: "CLEAN" (에이전트 관련 키워드 0건)
```

---

### Scenario 2: 루트 스크립트 6종 수록 검증

```bash
# 1. 실행 명령
for script in make_seed_pack.sh setup.sh start_server.sh status_server.sh stop_server.sh unpack_seed.sh; do
  grep -q "$script" README.md && echo "✓ $script verified" || echo "❌ $script missing";
done

# 2. 기대 결과
# - 6개 스크립트 모두 "✓ verified" 출력
```

---

### Scenario 3: 단위 테스트 회귀 검증

```bash
uv run pytest tests/unit/
```
