# Quickstart & End-to-End Validation Guide: 보조 모델 및 벤치마크 개선

**Feature**: `062-fix-aux-models-benchmark`
**Created**: 2026-07-31

## 1. 개요 (Overview)

본 가이드는 BGE M3 임베딩 모델, BGE Reranker v2 M3 리랭킹 모델 구동 정상화 및 품질 벤치마크 평가 후 기본 다중 모델 서빙(`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`)의 백그라운드 복원 조치를 실측 검증하는 절차를 설명합니다.

---

## 2. 사전 조건 (Prerequisites)

- 로컬 CUDA 환경 활성화 (`GeForce GTX 1070` 또는 동급 GPU)
- `uv` 패키지 매니저 및 가상환경 준비 완료 (`uv sync`)

---

## 3. 검증 시나리오 및 명령어 (Validation Scenarios)

### 시나리오 1: 전체 실측 품질 벤치마크 실행

```bash
uv run python scripts/benchmark_quality.py --auto-download --real
```

**기대 결과**:
1. `bge-m3` 단계: `[Step 4] ✅ 추론 완료 (Embedding Vector Generated)` 성공 출력 (`⚠️ 실측 추론 실패` 없음)
2. `bge-reranker-v2-m3` 단계: `[Step 3] ✅ 서빙 READY` 성공 및 `[Step 4] ✅ 추론 완료`
3. `Post-Benchmark` 단계: `[Post-Benchmark] ✅ 기본 모델 그룹 (qwen3.5-4b, bge-m3, bge-reranker-v2-m3) VRAM 복원 완료`

---

### 시나리오 2: 스크립트 종료 후 서버 상주 상태 검증

```bash
./status_server.sh
```

**기대 결과**:
- 프로세스 상태: `🟢 구동 중 (RUNNING, PID: xxx)`
- REST API 헬스체크 (http://0.0.0.0:8081/health): `{"status": "alive"}`
- 8090 포트 (`bge-m3`), 8091 포트 (`bge-reranker-v2-m3`) 서빙 프로세스 정상 구동 확인

---

### 시나리오 3: 전체 테스트 수트 회귀 검증

```bash
uv run pytest
```

**기대 결과**:
- 모든 단위/통합 테스트 수트 100% 통과 (Green Pass)
