# Quickstart Validation Guide: 자동 모델 다운로드 및 동적 서빙 프로세스 실행 관리

**Feature Branch**: `009-auto-model-download-serving`
**Date**: 2026-07-29

## Prerequisites

- Python 3.10+ & `uv` 패키지 매니저
- HuggingFace Hub 다운로드를 위한 네트워크 연결

---

## 1. 모델 다운로더 모듈 단위 테스트 실행

```bash
uv run pytest tests/unit/test_model_downloader.py
```

---

## 2. 원스톱 실측 벤치마크 및 자동 다운로드 구동

미존재 모델 자동 다운로드 및 실제 서빙 프로세스 개설 ➔ 실측 추론 ➔ 3D 보고서 생성을 원스톱 구동합니다.

```bash
# 원스톱 실측 벤치마크 (자동 다운로드 + 실측 연동)
uv run python scripts/benchmark_quality.py --auto-download --real
```

### Expected Output
- 미존재 가중치 자동 다운로드 진행률 표시
- `llama-server` 프로세스 로딩 및 GPU VRAM 실측 연동 (`nvtop`에서 부하 확인)
- 마크다운 분석 보고서(`specs/008-response-quality-eval/analysis_report_quality.md`) 갱신
