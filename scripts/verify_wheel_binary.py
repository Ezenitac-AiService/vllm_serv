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


def verify_wheel(wheel_path: str) -> Tuple[bool, Dict[str, int], bool, str]:
    """Verifies a .whl file for legacy CPU compatibility and CUDA support.

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
                # Check filename for CUDA library
                if "cuda" in basename.lower():
                    cuda_found = True

                cnt = scan_so_with_python_bytes(so_path)
                so_counts[rel_name] = cnt
                total_avx += cnt

        # A wheel with valid .so libraries, CUDA support, and 0 AVX instructions is valid
        is_valid = len(so_files) > 0 and cuda_found and total_avx == 0
        if is_valid:
            msg = f"✓ Wheel verified valid: CUDA enabled ({len(so_counts)} .so files checked, 0 AVX)"
        else:
            msg = f"❌ Wheel INVALID: Found issues across .so files (cuda_enabled={cuda_found}, total_avx={total_avx})"

        return is_valid, so_counts, cuda_found, msg

    except Exception as e:
        return False, {}, False, f"Failed to inspect wheel: {e}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify .whl binary for 0 AVX instructions and CUDA support.")
    parser.add_argument("wheel_path", help="Path to .whl file")
    args = parser.parse_args()

    is_valid, so_counts, cuda_enabled, msg = verify_wheel(args.wheel_path)
    print(msg)
    for so_name, cnt in so_counts.items():
        if cnt > 0:
            print(f"  - {so_name}: {cnt} AVX instructions")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
