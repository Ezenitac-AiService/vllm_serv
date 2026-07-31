# Quickstart Validation Guide: 시드 팩 배제 검증 (033-exclude-benchmark-cache-seed-pack)

## 1. 개요 (Overview)

본 가이드는 `make_seed_pack.sh` 실행을 통해 생성된 시드 팩 아카이브 내부에 기기 특정 벤치마크 캐시(`config/model_context_profiles.json`) 및 `.legacy/` 파일이 정상 배제되었는지 검증하는 절차입니다.

---

## 2. 검증 시나리오 A: 단위 테스트 구동

### 명령어 실행

```bash
uv run pytest tests/unit/test_seed_pack.py
```

### 기대 결과 (Expected Outcome)

- 시드 팩 필수 항목 포함 및 `config/model_context_profiles.json`, `.legacy/` 미함유 검증 테스트가 100% 통과합니다.

---

## 3. 검증 시나리오 B: 수동 아카이브 검증

### 명령어 실행

```bash
./scripts/make_seed_pack.sh
tar -tzf dist/vllm_serv_seed.tar.gz | grep -E "model_context_profiles|\.legacy|benchmark_results" || echo "✓ Exclusion Verified"
```

### 기대 결과 (Expected Outcome)

- 콘솔 출력: `✓ Exclusion Verified` (배제 항목 미감지 성공)
