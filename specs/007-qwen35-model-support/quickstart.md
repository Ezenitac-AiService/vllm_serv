# Quickstart Validation Guide: Qwen3.5 모델 연동 및 벤치마크 검증

이 가이드는 Qwen3.5 3종 모델(2B, 4B, 9B) 추가 및 기존 Gemma 4 모델 교차 벤치마크 검증 기능을 엔드투엔드로 구동하고 확인하는 절차를 설명합니다.

---

## 1. Qwen3.5 프리셋 바인딩 검증

### 1.1 대시보드 API 용량 조회 (Capabilities)
```bash
curl -s http://127.0.0.1:8000/dashboard/api/capabilities | jq .
```
- **기대 결과**: `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 프리셋 모델 및 VRAM 임계치가 결과 리스트에 표시됩니다.

### 1.2 Qwen3.5 모델 적용 API 호출
```bash
curl -X POST http://127.0.0.1:8000/dashboard/api/apply \
     -H "Content-Type: application/json" \
     -d '{"model_id": "qwen3.5-2b", "n_ctx": 4096}'
```
- **기대 결과**: `{"status": "success", "message": "Loading model..."}` 응답 및 SSE 이벤트로 `LOADING` ➔ `READY` 전이.

---

## 2. Qwen3.5 + Gemma 4 교차 벤치마크 자동화 구동

```bash
uv run python scripts/benchmark_qwen35.py
```

- **실행 결과**:
  1. Gemma 4 3종 (E2B, E4B, 12B) 및 Qwen3.5 3종 (2B, 4B, 9B x Q4_K_M, Q4_0, Q8_0) 벤치마크 자동 수행
  2. 로딩 시간(초), TTFT(ms), TPOT(tokens/s), 피크 VRAM(MB) 실측
  3. `specs/007-qwen35-model-support/analysis_report_qwen35.md` 분석 보고서 최종 생성

---

## 3. 단위/통합 레그레션 수트 실행

```bash
uv run pytest
```
- **기대 결과**: 13개 기존 테스트 + Qwen3.5 신규 테스트 포함 100% 통과 (0 failures).
