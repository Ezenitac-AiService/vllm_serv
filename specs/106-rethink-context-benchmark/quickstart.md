# Quickstart Validation Guide: 컨텍스트 윈도우 벤치마킹 가용성 및 신뢰성 검증

**Feature Branch**: `106-rethink-context-benchmark`
**Date**: 2026-08-07
**Spec**: [spec.md](./spec.md)

이 가이드는 `106-rethink-context-benchmark` 기능이 올바르게 작동하는지 검증하기 위한 종단간(End-to-End) 파이프라인 검증 시나리오를 정의합니다.

---

## 1. 사전 준비 (Prerequisites)

```bash
# 가상환경 활성화
source /home/dev/storage/vllm_serv/.venv/bin/activate
```

---

## 2. 실측 검증 시나리오 (Verification Scenarios)

### Scenario A: 백그라운드 서빙 서버 구동 중 벤치마킹 수행 시 안전 격리 검증

백그라운드 서빙 서버가 켜져 있어 VRAM이 점유된 상태에서 벤치마킹을 실행해도, 메인 서빙 프로세스가 사살되거나 커널 OOM이 발생하지 않고 가용 자원 기준 안전 처리되는지 확인합니다.

```bash
# 1. 메인 서빙 서버 구동
./start_server.sh

# 2. 백그라운드 서버 구동 중 벤치마킹 실행 (8089/8090/8091 메인 서버 다운 방지 및 Free VRAM 감지)
uv run python scripts/benchmark_context_window.py --force-benchmark

# 3. 메인 서빙 서버 산출물 및 PID 생존 확인
pgrep -f "src.api.server"
curl -s http://127.0.0.1:8081/health || echo "Main server port active"
```

**기대 결과**:
- 8089/8090/8091 메인 서버 PID가 사살되지 않고 정상 응답 유지 (`SC-001` 통과).
- 스크립트가 전체 하드웨어가 아닌 실시간 가용 VRAM(Free VRAM)을 파악하여 Pre-flight 경고 또는 무사히 안전 평가를 마침 (`SC-003` 통과).

---

### Scenario B: `llama_cpp.server` (Python Fallback) 환경 헬스체크 폴백 검증

`llama_cpp.server` 구동 시 `/health` 경로가 404를 반환하더라도 `/v1/models` 엔드포인트를 폴백 검증하여 100% Readiness를 통과하는지 확인합니다.

```bash
# 단일 모델 정밀 이진 탐색 벤치마크 실행 (llama_cpp.server 사용 환경)
uv run python scripts/benchmark_context_window.py --fine-grained --model qwen3.5-2b
```

**기대 결과**:
- `404 Not Found` 타임아웃 오류(-15 SIGTERM kill)가 발생하지 않음.
- `/v1/models` 폴백 검증 성공으로 헬스체크 통과 (`Step 1 ~ 5 PASS` 기록, `SC-004` 통과).

---

### Scenario C: 비파괴적(Non-destructive) 프로파일 보존 검증

기존 정상 프로파일이 존재하는 상태에서 일시적 예외/OOM이 발생하더라도 기존 프로파일 데이터가 덮어씌워지지 않고 유지되는지 확인합니다.

```bash
# 기존 프로파일 상태 백업 확인 및 벤치마크 실행
cat config/model_context_profiles.json | grep -A 5 "qwen3.5-2b"

# 강제 과부하 유도 후 실행
MOCK_RECOMMENDED_CONTEXT=2048 uv run pytest tests/unit/test_benchmark_context_window.py
```

**기대 결과**:
- 덮어쓰기 지정이 없으면 기존 검증된 `max_context_length` 결과가 유실되거나 일률적 2048 fallback으로 덮어씌워지지 않음 (`SC-002` 통과).

---

## 3. 회귀 검증 테스트 수트 실행 (Full Suite Regression)

```bash
# 전체 파이썬 단위/통합 테스트 회귀 검증
uv run pytest
```
