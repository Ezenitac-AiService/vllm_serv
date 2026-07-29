# Quickstart Validation Guide: 모델 답변 품질 비교 분석 및 자동 검증 (Response Quality Evaluation)

**Feature Branch**: `008-response-quality-eval`
**Date**: 2026-07-29

## Prerequisites

- Python 3.10+ & `uv` 패키지 매니저
- 프로젝트 루트: `/home/dev/storage/vllm_serv/`

---

## 1. 품질 평가 엔진 단위 테스트 실행 (Mock Mode)

CI/CD 및 빠른 품질 가중치 계산 수식 검증을 위해 `uv run pytest` 명령어를 실행합니다.

```bash
# 빠른 단위/통합 품질 검증 수트 실행
uv run pytest tests/unit/test_quality_evaluator.py tests/integration/test_quality_benchmark.py
```

### Expected Output
- 모든 테스트 케이스 통과 (`PASSED`)
- 가중 채점 알고리즘 (`Quality Score = 0.6 * Quantitative + 0.4 * Qualitative`) 정상 동작 검증

---

## 2. 종합 답변 품질 벤치마크 및 3D 보고서 자동 생성 (Benchmark Mode)

Qwen 3.5 3종 및 Gemma 4 3종 모델에 대한 [속도 + VRAM + 품질 점수 + ATEAM/BTEAM 벤치마크 수행력] 교차 벤치마크를 구동하고 마크다운 보고서를 갱신합니다.

```bash
# 3차원 종합 품질 벤치마크 스크립트 실행
uv run python scripts/benchmark_quality.py
```

### Expected Output
```text
[Quality Benchmark] Starting Qwen 3.5 & Gemma 4 cross-model quality & efficiency evaluation...
[Quality Benchmark] Report generated successfully at specs/008-response-quality-eval/analysis_report_quality.md
```

### Generated Report Inspection

생성된 분석 보고서 파일 [analysis_report_quality.md](file:///home/dev/storage/vllm_serv/specs/008-response-quality-eval/analysis_report_quality.md)를 확인합니다.

```bash
cat specs/008-response-quality-eval/analysis_report_quality.md
```

- **최적 가성비 모델 추천** (`Quality-per-Speed Index` 및 `Quality-per-VRAM Index` 기반)
- **Gemma 4 vs Qwen 3.5 상대 품질 점수 비교표**
- **ATEAM(주식 댓글) / BTEAM(음식점 리뷰) 태스크 슬롯 추출 정확도(Slot Precision) 수치**
