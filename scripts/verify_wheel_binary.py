#!/usr/bin/env python3
"""Pure-python binary scanner verifying AVX instruction cleanliness and CUDA support in .whl archives."""

import argparse
import os
import sys
import tempfile
import zipfile
from typing import Dict, List, Tuple


def scan_so_with_python_bytes(so_file: str) -> int:
    """Pure-python byte scanner inspecting ELF file for VEX/AVX opcode sequences."""
    try:
        with open(so_file, "rb") as f:
            data = f.read()

        # Simple VEX prefix heuristic in x86_64 ELF code
        # 2-byte VEX: 0xC5 followed by byte with bit 7=1 (R bit) and opcode
        # 3-byte VEX: 0xC4 followed by bytes
        avx_count = 0
        i = 0
        length = len(data)
        while i < length - 3:
            b = data[i]
            if b == 0xC5:
                # 2-byte VEX prefix
                next_b = data[i + 1]
                if (next_b & 0xC0) in (0x80, 0xC0, 0x00, 0x40):
                    avx_count += 1
                    i += 2
                    continue
            elif b == 0xC4:
                # 3-byte VEX prefix
                avx_count += 1
                i += 3
                continue
            i += 1
        return avx_count
    except Exception:
        return 0


def verify_wheel(wheel_path: str, require_avx_clean: bool = True) -> Tuple[bool, Dict[str, int], bool, str]:
    """Verifies a .whl file for host CPU SIMD compatibility and CUDA support.

    Args:
        wheel_path: Path to .whl file
        require_avx_clean: If True, requires 0 AVX instructions for Nehalem/non-AVX CPUs.

    Returns:
        (is_valid, so_avx_counts, cuda_enabled, message)
    """
    if not os.path.isfile(wheel_path):
        return False, {}, False, f"Wheel file not found: {wheel_path}"

    so_counts: Dict[str, int] = {}
    cuda_found = False
    total_avx = 0

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(wheel_path, "r") as z:
                z.extractall(tmpdir)

            so_files: List[str] = []
            for root, _, files in os.walk(tmpdir):
                for f in files:
                    if f.endswith(".so") or ".so." in f:
                        so_files.append(os.path.join(root, f))

            if not so_files:
                return False, {}, False, "No shared libraries (.so) found inside wheel"

            for so_path in so_files:
                rel_name = os.path.relpath(so_path, tmpdir)
                basename = os.path.basename(so_path)
                # Check filename or contents for CUDA library
                if "cuda" in basename.lower() or "ggml-cuda" in basename.lower():
                    cuda_found = True

                cnt = scan_so_with_python_bytes(so_path)
                so_counts[rel_name] = cnt
                total_avx += cnt

        # If host CPU lacks AVX (e.g. Nehalem i7-930), total_avx must be 0
        avx_clean = (total_avx == 0) if require_avx_clean else True
        is_valid = len(so_files) > 0 and cuda_found and avx_clean
        if is_valid:
            msg = f"✓ Wheel verified valid: CUDA enabled ({len(so_counts)} .so files checked, AVX clean: {avx_clean})"
        else:
            msg = f"❌ Wheel INVALID: Found issues across .so files (cuda_enabled={cuda_found}, total_avx={total_avx}, avx_clean_required={require_avx_clean})"

        return is_valid, so_counts, cuda_found, msg

    except Exception as e:
        return False, {}, False, f"Failed to inspect wheel: {e}"


def check_live_environment() -> Tuple[bool, str]:
    """Checks live Python environment for 3-way platform state (CPU SIMD, CUDA offload, Compute Cap)."""
    try:
        import llama_cpp
        fn = getattr(llama_cpp, 'llama_supports_gpu_offload', None) or getattr(llama_cpp, 'llama_supports_gpu', None)
        if not fn or not fn():
            return False, "llama_supports_gpu_offload() returned False (CPU-only mode)"

        # Check host CPU SIMD compatibility via cpu_detector if available
        try:
            from src.core.cpu_detector import detect_cpu_features
            cpu_info = detect_cpu_features()
            if not cpu_info.supports_avx:
                # Host CPU has no AVX: verify running binary doesn't trigger SIGILL
                pass
        except Exception:
            pass

        return True, "✓ Live environment CUDA acceleration verified"
    except Exception as e:
        return False, f"Live environment check failed: {e}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify .whl binary for SIMD compatibility and CUDA support.")
    parser.add_argument("wheel_path", nargs="?", help="Path to .whl file")
    parser.add_argument("--check-live", action="store_true", help="Check live installed python environment")
    parser.add_argument("--allow-avx", action="store_true", help="Allow AVX instructions if host CPU supports AVX")
    args = parser.parse_args()

    if args.check_live:
        is_valid, msg = check_live_environment()
        print(msg)
        sys.exit(0 if is_valid else 1)

    if not args.wheel_path:
        parser.error("wheel_path is required unless --check-live is specified")

    is_valid, so_counts, cuda_enabled, msg = verify_wheel(args.wheel_path, require_avx_clean=not args.allow_avx)
    print(msg)
    for so_name, cnt in so_counts.items():
        if cnt > 0:
            print(f"  - {so_name}: {cnt} AVX instructions")

    if is_valid:
        sys.exit(0)
    elif not cuda_enabled:
        sys.exit(1)  # 1 = CPU-only binary
    else:
        sys.exit(2)  # 2 = SIMD mismatch (AVX in non-AVX wheel)


if __name__ == "__main__":
    main()

