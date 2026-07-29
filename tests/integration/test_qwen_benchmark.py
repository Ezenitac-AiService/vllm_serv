import os
import pytest
from scripts.benchmark_qwen35 import QwenBenchmarkRunner

def test_qwen_benchmark_runner_execution():
    """T011 / US2: Test benchmark runner execution and report generation."""
    test_report_path = "specs/007-qwen35-model-support/test_analysis_report_qwen35.md"
    runner = QwenBenchmarkRunner(output_report_path=test_report_path)
    runner.run_all()

    assert os.path.exists(test_report_path)
    assert len(runner.results) > 0

    with open(test_report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Qwen3.5 및 Gemma 4 모델 교차 성능 분석 보고서" in content
    assert "qwen3.5-4b" in content

    # Cleanup temporary test report file
    if os.path.exists(test_report_path):
        os.remove(test_report_path)
