# Quickstart Guide: 코드베이스 리팩토링 및 레거시 아카이브 검증 (026-archive-legacy-files)

## 1. Prerequisites

- Python 3.12+ 및 `uv` 환경
- Git 저장소 가용 상태

---

## 2. Validation Steps

### Step 1: `.legacy/` 아카이브 디렉토리 및 파일 이동 검증

```bash
# .legacy 디렉토리 존재 및 파일 이동 확인
ls -la .legacy/
```

**Expected Outcome**:
- `.legacy/` 하위에 `ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`, `get-pip.py`, `benchmark_results.json`, 루트 스텁 셸 스크립트들이 안전하게 아카이빙되어 존재함.

### Step 2: 전체 Pytest 회귀 테스트 수행

```bash
uv run pytest tests/
```

**Expected Outcome**:
- 143+ 개 단위 및 통합 테스트 전원 통과 (**100% PASS**).
