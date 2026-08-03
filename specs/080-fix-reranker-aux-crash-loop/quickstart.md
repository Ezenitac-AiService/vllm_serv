# Quickstart: 보조 모델 크래시 루프 방지 및 503 프록시 게이트 검증 (`080-fix-reranker-aux-crash-loop`)

본 가이드는 Feature 080 구현 사항을 검증하는 실행 절차를 안내합니다.

## 사전 조건 (Prerequisites)

- 파이썬 가상환경 (`uv run pytest`)
- `samples/config.json` 설정 파일 존재

## 검증 시나리오 (Validation Scenarios)

### 1. 보조 모델 연속 크래시 시 서킷 브레이커(DISABLED 전이) 검증

```bash
# 3회 연속 크래시 후 DISABLED 상태로 전환되고 추가 재시작 시도가 중단되는지 검증
uv run pytest tests/unit/test_auxiliary_circuit_breaker.py -v
```

**기대 결과**:
- 보조 프로세스가 3회 연속 실패하면 `ProcessStatusEnum.DISABLED`로 전이
- `_crash_recovery_loop`에서 해당 포트에 대해 더 이상 `spawn_process()`를 호출하지 않음
- `consecutive_crashes`가 3에 고정됨

### 2. 보조 모델 DISABLED / ERROR 상태 시 HTTP 503 응답 검증

```bash
# 보조 모델 미구동 또는 DISABLED 상태에서 /v1/rerank 및 /v1/embeddings 호출 시 503 반환 검증 (404 발생 0건)
uv run pytest tests/integration/test_auxiliary_503_gate.py -v
```

**기대 결과**:
- `POST /v1/rerank` 호출 시 404가 아닌 `503 Service Unavailable` 반환
- 응답 JSON `{"detail": "Reranker model is not available..."}` 포함
- `POST /v1/embeddings` 호출 시 동일하게 `503 Service Unavailable` 반환

### 3. 보조 모델 순차 초기화 (Sequential Initialization) 검증

```bash
# start_auto_startup_and_recovery() 호출 시 Embedding 후 Reranker가 순차적으로 구동되는지 검증
uv run pytest tests/unit/test_auxiliary_sequential_init.py -v
```

**기대 결과**:
- Embedding 구동 완료(READY) 전까지 Reranker spawn이 대기함

### 4. 전체 수트 회귀 테스트 (Full Suite Regression Rule)

```bash
# 헌법 VII조에 따른 전체 테스트 수트 검증
uv run pytest tests/ -v
```

**기대 결과**:
- 전체 테스트 100% 통과 (Green Pass)
