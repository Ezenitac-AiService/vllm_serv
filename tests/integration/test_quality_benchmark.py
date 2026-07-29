"""
Integration tests for 3D Quality-Speed-VRAM Benchmark Runner and Report Generator.
"""

import os
import pytest
from scripts.benchmark_quality import run_benchmark, generate_markdown_report


def test_run_benchmark_execution():
    """Verify that run_benchmark computes metrics for all 6 models."""
    reports = run_benchmark()
    assert len(reports) == 6
    model_ids = [r.model_id for r in reports]
    assert "Qwen 3.5 2B" in model_ids
    assert "Qwen 3.5 4B" in model_ids
    assert "Qwen 3.5 9B" in model_ids
    assert "Gemma 4 E2B" in model_ids
    assert "Gemma 4 E4B" in model_ids
    assert "Gemma 4 12B" in model_ids

    for r in reports:
        assert 1.0 <= r.avg_quality_score <= 5.0
        assert r.quality_per_speed_index > 0.0
        assert r.quality_per_vram_index > 0.0


def test_markdown_report_generation(tmp_path):
    """Verify markdown report file generation and content structure."""
    reports = run_benchmark()
    test_report_path = os.path.join(tmp_path, "analysis_report_quality.md")
    
    generate_markdown_report(reports, test_report_path)
    assert os.path.exists(test_report_path)

    with open(test_report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# Qwen 3.5 vs Gemma 4 3차원 종합 품질-속도-VRAM 교차 비교 분석 보고서" in content
    assert "Quality/Speed Index" in content
    assert "Quality/VRAM Index" in content
    assert "Qwen 3.5 4B" in content
    assert "Gemma 4 12B" in content
