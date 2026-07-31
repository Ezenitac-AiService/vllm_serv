# Quickstart Validation Guide: GPU CUDA Acceleration & VRAM Load Validation

**Feature Branch**: `010-gpu-cuda-vram-validation`
**Date**: 2026-07-29

---

## 1. Prerequisites & Environment Check

```bash
# 1. NVIDIA GPU 및 CUDA 가속 상태 확인
nvidia-smi

# 2. CUDA 가속 llama-cpp-python 확인
uv run python -c "import llama_cpp; print('GPU support:', llama_cpp.llama_supports_gpu())"
```

---

## 2. Validation Scenarios

### Scenario A: GPU/CUDA 검증기 단위 테스트
```bash
uv run pytest tests/unit/test_gpu_detector.py -v
```

### Scenario B: CPU Fallback 사전 차단 검증
```bash
# CPU 전용 모드 강제 시 GpuAccelerationError 예외 발생 확인
MOCK_CPU_ONLY=1 uv run pytest tests/integration/test_gpu_validation.py -v
```

### Scenario C: 100% GPU VRAM 오프로드 원스톱 벤치마크 실행
```bash
uv run python scripts/benchmark_quality.py --auto-download --real-inference
```
**Expected Outcome**:
- `nvidia-smi`를 통해 GTX 1080 Ti GPU VRAM 메모리가 점유되고 GPU Util이 발생하는지 확인.
- 6종 모델 추론 속도(TPOT)가 30 tok/s 이상 측정되고 `analysis_report_quality.md` 생성 완수.
