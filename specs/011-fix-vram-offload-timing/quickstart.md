# Quickstart: GPU VRAM Offload & Process Lifecycle Timing Fix Validation Guide

## Runnable Validation Scenarios

### Scenario 1: Verify READY state is delayed until 100% VRAM offload is complete

Run unit and integration tests verifying `LlamaManager._wait_for_ready()` waits for VRAM offload status:

```bash
uv run pytest tests/unit/test_gpu_detector.py tests/integration/test_gpu_validation.py -v
```

**Expected Outcome**: All tests pass. `ProcessState` remains `LOADING` until `vram_offloaded=True`.

### Scenario 2: Validate 100% GPU VRAM inference and default model restoration post-benchmark

Execute the one-stop real benchmark runner:

```bash
uv run python scripts/benchmark_quality.py --auto-download --real
```

**Expected Outcome**:
1. `[Step 2]` shows `[ProcessManager] FR-004: VRAM 해제 검증 완료: 성공`.
2. `[Step 3]` HTTP health check waits until VRAM offloading is complete.
3. `[Step 4]` Real GPU inference completes with TTFT < 1.0s and TPOT > 30 tok/s (no CPU fallback or timeouts).
4. `[Step 6]` Process terminates and VRAM is returned cleanly before moving to the next model.
5. **Post-Benchmark Restoration**: After all models are evaluated, the default resident model (`qwen3.5-4b`) is automatically re-loaded into VRAM to resume normal production serving.
