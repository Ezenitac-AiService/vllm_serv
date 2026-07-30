# Contract Specification: Wheel Binary Scanner & Diagnostic API

## Component Overview

`scripts/verify_wheel_binary.py` (또는 `src/core/wheel_scanner.py`)는 파이썬 내장 모듈만을 사용하여 `.whl` 패키지 내부의 모든 `.so` 공유 라이브러리를 전수 스캔하고 AVX 명령어 수(0개) 및 CUDA 수용성을 검증하는 파이썬 유틸리티 계약입니다.

## Python API Contract

```python
class WheelBinaryScanner:
    """Pure-python binary scanner verifying AVX instruction cleanliness and CUDA support in .whl archives."""

    def __init__(self, wheel_path: str):
        """Initializes scanner with target .whl filepath."""
        ...

    def scan_wheel(self) -> WheelScanReport:
        """Parses zip entries, decodes .so files, scans for VEX prefix and AVX opcodes.

        Returns:
            WheelScanReport with is_valid, scanned_so_files, avx_instruction_count, and cuda_enabled.
        """
        ...
```

## CLI Contract

```bash
# Exit code 0: Wheel is valid (AVX == 0 and CUDA supported)
# Exit code 1: Wheel is invalid (AVX > 0 or corrupted or missing CUDA)
python3 scripts/verify_wheel_binary.py wheels/legacy_i7_930/llama_cpp_python-0.3.34-py3-none-linux_x86_64.whl
```

## Expected Behavior & Edge Cases

1. **정상 휠 검증 통과**:
   - `libggml-cpu.so`, `libggml-cuda.so` 등 모든 내부 `.so` 아티팩트의 AVX 명령어 수가 0개이면 stdout에 `✓ Wheel verification passed (AVX=0, CUDA=OK)` 출력 및 종료 코드 `0` 반환.

2. **AVX 오염 휠 감지**:
   - `libggml-cpu.so` 등에 AVX 명령어(예: 4,307개)가 발견되면 `✗ Wheel verification FAILED: Found 4307 AVX instructions in libggml-cpu.so` 출력 및 종료 코드 `1` 반환.

3. **외부 CLI 도구 미의존성**:
   - `objdump`, `nm`, `readelf` 등 외부 바이너리 유틸리티가 설치되지 않은 환경에서도 파이썬 `zipfile` 및 `struct` 모듈만으로 100% 동일하게 검증 수행.
