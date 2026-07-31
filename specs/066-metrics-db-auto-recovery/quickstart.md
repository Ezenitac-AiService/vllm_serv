# Quickstart & End-to-End Validation Guide: MetricsDB 자가 복구 (066-metrics-db-auto-recovery)

**Feature**: `066-metrics-db-auto-recovery`

## 1. 개요 (Overview)

본 가이드는 손상된 `data/metrics.db` 파일이 존재할 때 `MetricsDB` 초기화가 실패 없이 자가 복구(Auto-Healing)되는지 독립 실측 검증하는 가이드입니다.

---

## 2. 검증 시나리오 (Validation Scenarios)

### 시나리오 1: 손상된 DB 파일 주입 및 서버 자가 복구 실측
```bash
# 1. 고의로 metrics.db 헤더 훼손
echo "INVALID_MALFORMED_SQLITE_HEADER_DATA" > data/metrics.db

# 2. MetricsDB 초기화 및 회귀 테스트 구동
uv run pytest tests/unit/test_metrics_db.py -k test_metrics_db_corrupt_recovery
```
**기대 결과**:
- `data/metrics.db.corrupt_*` 백업 파일 생성 확인
- `data/metrics.db` 신규 정상 DB 재창조 확인
- Pytest 단일 및 회귀 테스트 100% Green Pass

---

### 시나리오 2: 전체 단위/통합 테스트 회귀 검증
```bash
uv run pytest
```
**기대 결과**: 100% Green Pass 통과
