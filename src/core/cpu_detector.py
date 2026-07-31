"""
CPU Feature & GPU Capability Detector for llama.cpp CMake Build Pipeline.
Detects CPU SIMD instruction set support (AVX, AVX2, F16C, FMA) and GPU Compute Capability (sm_61, sm_86, etc.)
to dynamically select non-crashing build flags for llama-server and llama-cpp-python.
"""

import os
import re
import sys
import shutil
import argparse
import subprocess
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from src.core.gpu_detector import GpuAccelerationError


class CpuFeatureInfo(BaseModel):
    """CPU Hardware & SIMD Instruction Set Capabilities."""
    model_name: str = Field(default="Unknown CPU", description="CPU Model identifier")
    architecture: str = Field(default="x86_64", description="CPU Architecture")
    vendor_id: str = Field(default="Unknown", description="CPU Vendor ID")
    flags: List[str] = Field(default_factory=list, description="Supported SIMD instruction set flags")
    supports_sse4_2: bool = Field(default=False, description="SSE4.2 support")
    supports_avx: bool = Field(default=False, description="AVX support")
    supports_avx2: bool = Field(default=False, description="AVX2 support")
    supports_f16c: bool = Field(default=False, description="F16C support")
    supports_fma: bool = Field(default=False, description="FMA support")
    is_fallback: bool = Field(default=False, description="Safe fallback mode triggered due to inspection failure")


class GpuCapabilityInfo(BaseModel):
    """NVIDIA GPU Device & Compute Capability Info."""
    gpu_name: str = Field(default="NVIDIA GPU", description="GPU Device Name")
    compute_capability: str = Field(default="8.6", description="Compute Capability (e.g. 6.1, 8.6)")
    cuda_arch_code: str = Field(default="86", description="CMake CUDA Architecture Code (e.g. 61, 86)")
    total_vram_mb: int = Field(default=0, description="Total VRAM in MB")


class LlamaCppBuildFlags(BaseModel):
    """Generated CMake build flags for llama.cpp compilation."""
    ggml_cuda: bool = Field(default=True, description="Enable CUDA backend (always True)")
    ggml_avx: bool = Field(default=True, description="GGML_AVX CMake option")
    ggml_avx2: bool = Field(default=True, description="GGML_AVX2 CMake option")
    ggml_f16c: bool = Field(default=True, description="GGML_F16C CMake option")
    ggml_fma: bool = Field(default=True, description="GGML_FMA CMake option")
    cuda_architectures: str = Field(default="86", description="CMAKE_CUDA_ARCHITECTURES option")
    cmake_args_list: List[str] = Field(default_factory=list, description="List of CMake arguments")
    cmake_args_str: str = Field(default="", description="Space-separated CMake arguments string")


class TargetPlatformProfile(BaseModel):
    """Hardware Profile Entity."""
    profile_id: str
    name: str
    cpu_model: str
    ram_gb: int
    gpu_name: str
    vram_mb: int
    compute_capability: str
    os_name: str
    expected_avx: bool
    expected_avx2: bool = True



def detect_cpu_features(cpuinfo_path: str = "/proc/cpuinfo") -> CpuFeatureInfo:
    """
    FR-001 & FR-004: Inspects host CPU features via /proc/cpuinfo or sysctl.
    Falls back to safe conservative mode (all extensions OFF) if /proc/cpuinfo is unreadable.
    """
    model_name = "Unknown CPU"
    vendor_id = "Unknown"
    flags: List[str] = []

    try:
        if os.path.exists(cpuinfo_path):
            with open(cpuinfo_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            for line in content.splitlines():
                if line.startswith("model name") and model_name == "Unknown CPU":
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        model_name = parts[1].strip()
                elif line.startswith("vendor_id") and vendor_id == "Unknown":
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        vendor_id = parts[1].strip()
                elif line.startswith("flags") or line.startswith("Features"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        flags = parts[1].strip().split()

            flags_lower = [f.lower() for f in flags]
            supports_sse4_2 = "sse4_2" in flags_lower or "sse4.2" in flags_lower or "sse4_1" in flags_lower
            supports_avx = "avx" in flags_lower
            supports_avx2 = "avx2" in flags_lower
            supports_f16c = "f16c" in flags_lower
            supports_fma = "fma" in flags_lower

            return CpuFeatureInfo(
                model_name=model_name,
                architecture="x86_64",
                vendor_id=vendor_id,
                flags=flags,
                supports_sse4_2=supports_sse4_2,
                supports_avx=supports_avx,
                supports_avx2=supports_avx2,
                supports_f16c=supports_f16c,
                supports_fma=supports_fma,
                is_fallback=False
            )
    except Exception as e:
        print(f"[CpuDetector] Warning: Failed to read {cpuinfo_path}: {e}. Triggering safe fallback mode.")

    # Safe conservative fallback mode (All SIMD extensions disabled)
    return CpuFeatureInfo(
        model_name="Fallback x86_64 CPU",
        architecture="x86_64",
        vendor_id="Unknown",
        flags=[],
        supports_sse4_2=True,
        supports_avx=False,
        supports_avx2=False,
        supports_f16c=False,
        supports_fma=False,
        is_fallback=True
    )


def detect_gpu_capability() -> GpuCapabilityInfo:
    """
    FR-007 & FR-009: Inspects host NVIDIA GPU compute capability via nvidia-smi.
    Raises GpuAccelerationError if nvidia-smi or active GPU is missing (fail-fast).
    """
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        raise GpuAccelerationError(
            "NVIDIA GPU 드라이버(nvidia-smi)를 찾을 수 없습니다.\n"
            "GPU 가속 서빙을 위해 NVIDIA GPU 드라이버 및 CUDA Toolkit 설치가 필수입니다.\n"
            "CPU 전용 빌드는 허용되지 않습니다."
        )

    try:
        # Query compute capability and GPU name
        cmd = [
            nvidia_smi,
            "--query-gpu=name,compute_cap,memory.total",
            "--format=csv,noheader,nounits"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        if not lines or not lines[0]:
            raise GpuAccelerationError("nvidia-smi에서 활성 NVIDIA GPU를 찾을 수 없습니다.")

        parts = [p.strip() for p in lines[0].split(",")]
        gpu_name = parts[0] if len(parts) > 0 else "NVIDIA GPU"
        raw_cap = parts[1] if len(parts) > 1 else "8.6"
        vram_mb = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 8192

        # Convert compute_cap string (e.g. "6.1" -> "61", "8.6" -> "86")
        arch_code = raw_cap.replace(".", "").strip()
        if not arch_code.isdigit():
            arch_code = "86"

        return GpuCapabilityInfo(
            gpu_name=gpu_name,
            compute_capability=raw_cap,
            cuda_arch_code=arch_code,
            total_vram_mb=vram_mb
        )
    except subprocess.CalledProcessError as e:
        raise GpuAccelerationError(f"nvidia-smi 실행에 실패했습니다: {e}")
    except Exception as e:
        if isinstance(e, GpuAccelerationError):
            raise e
        raise GpuAccelerationError(f"GPU 가속 장치 감지 실패: {str(e)}")


def detect_gpu_capability_safe() -> GpuCapabilityInfo:
    """
    Safely attempts GPU capability detection via nvidia-smi.
    Falls back to safe default (Compute Capability 6.1 / sm_61) on failure/missing driver.
    """
    try:
        return detect_gpu_capability()
    except Exception as e:
        print(f"[CpuDetector] Warning: GPU detection via nvidia-smi failed ({e}). Falling back to safe default GPU profile (sm_61).")
        return GpuCapabilityInfo(
            gpu_name="Fallback NVIDIA GPU",
            compute_capability="6.1",
            cuda_arch_code="61",
            total_vram_mb=8192
        )


def get_llama_build_flags(cpuinfo_path: str = "/proc/cpuinfo") -> LlamaCppBuildFlags:
    """
    FR-001, FR-002, FR-003, FR-004: Combines CPU & GPU inspection to generate exact CMake arguments.
    Falls back safely if nvidia-smi or /proc/cpuinfo fails.
    """
    cpu_info = detect_cpu_features(cpuinfo_path=cpuinfo_path)
    gpu_info = detect_gpu_capability_safe()

    avx_flag = "ON" if cpu_info.supports_avx else "OFF"
    avx2_flag = "ON" if cpu_info.supports_avx2 else "OFF"
    f16c_flag = "ON" if cpu_info.supports_f16c else "OFF"
    fma_flag = "ON" if cpu_info.supports_fma else "OFF"
    arch_code = gpu_info.cuda_arch_code

    args_list = [
        "-DGGML_CUDA=ON",
        f"-DGGML_AVX={avx_flag}",
        f"-DGGML_AVX2={avx2_flag}",
        f"-DGGML_F16C={f16c_flag}",
        f"-DGGML_FMA={fma_flag}",
        f"-DCMAKE_CUDA_ARCHITECTURES={arch_code}"
    ]

    args_str = " ".join(args_list)

    return LlamaCppBuildFlags(
        ggml_cuda=True,
        ggml_avx=cpu_info.supports_avx,
        ggml_avx2=cpu_info.supports_avx2,
        ggml_f16c=cpu_info.supports_f16c,
        ggml_fma=cpu_info.supports_fma,
        cuda_architectures=arch_code,
        cmake_args_list=args_list,
        cmake_args_str=args_str
    )



def match_platform_profile(cpuinfo_path: str = "/proc/cpuinfo") -> str:
    """
    FR-001 & FR-003: Matches detected hardware against config/platform_profiles.json profiles.
    Evaluates both GPU Compute Capability and CPU AVX/AVX2 support.
    Returns matching profile_id string (e.g. 'pascal-avx2-gtx1080ti', 'legacy-i7-930-gtx1070', 'dev-rtx3060').
    """
    try:
        from src.core.config_manager import ConfigManager
        cm = ConfigManager()
        profiles = cm.get_platform_profiles()
    except Exception:
        profiles = {}

    cpu_info = detect_cpu_features(cpuinfo_path=cpuinfo_path)
    try:
        gpu_info = detect_gpu_capability()
        cc = gpu_info.compute_capability
    except Exception:
        cc = "unknown"

    # 1. Exact match: GPU Compute Capability + CPU AVX2/AVX flags
    for pid, profile in profiles.items():
        prof_cc = str(profile.get("compute_capability", ""))
        prof_avx2 = profile.get("expected_avx2", True)
        prof_avx = profile.get("expected_avx", True)

        if prof_cc and prof_cc == cc:
            if cpu_info.supports_avx2 == prof_avx2 and cpu_info.supports_avx == prof_avx:
                return pid

    # 2. Fallback match by Compute Capability and AVX2 availability
    for pid, profile in profiles.items():
        prof_cc = str(profile.get("compute_capability", ""))
        if prof_cc and prof_cc == cc:
            prof_avx2 = profile.get("expected_avx2", False)
            if cpu_info.supports_avx2 == prof_avx2:
                return pid

    # 3. Default fallback heuristic
    if cc == "6.1" and cpu_info.supports_avx2:
        return "pascal-avx2-gtx1080ti"
    elif cc == "6.1" and not cpu_info.supports_avx:
        return "legacy-i7-930-gtx1070"
    elif cc == "8.6":
        return "dev-rtx3060"

    return "custom-hardware-profile"



def check_hardware_preflight(cpuinfo_path: str = "/proc/cpuinfo") -> Dict[str, Any]:
    """
    FR-002: Performs pre-flight checks before server daemonization.
    Verifies GPU driver (nvidia-smi) and CUDA compiler (nvcc).
    """
    results = {
        "passed": False,
        "nvidia_smi": False,
        "nvcc": False,
        "gpu_info": None,
        "error_message": "",
        "remediation_guide": ""
    }

    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        msg = (
            "❌ [Pre-flight Fail] NVIDIA GPU 드라이버(nvidia-smi)가 설치되어 있지 않거나 PATH에 없습니다.\n"
            "   해결 가이드: NVIDIA GPU 드라이버를 설치하고 `nvidia-smi` 커맨드가 작동하는지 확인하세요.\n"
            "   `sudo apt install nvidia-driver-535` 또는 공식 드라이버를 설치해야 합니다."
        )
        results["error_message"] = msg
        results["remediation_guide"] = "NVIDIA 드라이버 설치 필요: sudo apt install nvidia-driver-535"
        return results
    results["nvidia_smi"] = True

    nvcc = shutil.which("nvcc")
    if not nvcc:
        cuda_home = os.environ.get("CUDA_HOME") or "/usr/local/cuda"
        if os.path.exists(os.path.join(cuda_home, "bin", "nvcc")):
            nvcc = os.path.join(cuda_home, "bin", "nvcc")

    if not nvcc:
        msg = (
            "❌ [Pre-flight Fail] CUDA Compiler (nvcc)를 찾을 수 없습니다.\n"
            "   해결 가이드: CUDA Toolkit 12.x 이상을 설치하거나 PATH 환경변수에 nvcc 경로를 추가하세요.\n"
            "   예: export PATH=/usr/local/cuda/bin:$PATH"
        )
        results["error_message"] = msg
        results["remediation_guide"] = "CUDA Toolkit 설치 및 PATH 추가 필요: export PATH=/usr/local/cuda/bin:$PATH"
        return results
    results["nvcc"] = True

    try:
        gpu_info = detect_gpu_capability()
        results["gpu_info"] = gpu_info.model_dump()

        # FR-004 / US2: llama-cpp-python package CUDA offload support check
        try:
            import llama_cpp
            fn = getattr(llama_cpp, 'llama_supports_gpu_offload', None) or getattr(llama_cpp, 'llama_supports_gpu', None)
            if not fn or not fn():
                msg = (
                    "❌ [Pre-flight Fail] llama-cpp-python 패키지가 CUDA GPU 가속을 지원하지 않습니다 (CPU 전용 모드).\n"
                    "   해결 가이드: ./setup.sh를 다시 실행하여 CUDA 최적화 C++ 컴파일 파이프라인을 완료하세요."
                )
                results["error_message"] = msg
                results["remediation_guide"] = "./setup.sh 실행하여 llama-cpp-python CUDA 재컴파일 수행 필요"
                return results
            results["llama_gpu_offload"] = True
        except Exception as e:
            msg = f"❌ [Pre-flight Fail] llama-cpp-python 로드/검증 중 오류 발생: {e}"
            results["error_message"] = msg
            results["remediation_guide"] = "./setup.sh 실행하여 환경을 재설정하세요."
            return results

        results["passed"] = True
    except GpuAccelerationError as e:
        results["error_message"] = f"❌ [Pre-flight Fail] GPU 가속 검증 실패: {e}"
        results["remediation_guide"] = "GPU 인식 및 드라이버 동작 상태를 nvidia-smi로 점검하세요."

    return results


def print_detection_report(cpuinfo_path: str = "/proc/cpuinfo") -> None:
    """FR-005: Prints human-readable hardware detection and selected CMake build flags report."""
    cpu_info = detect_cpu_features(cpuinfo_path=cpuinfo_path)
    gpu_info = detect_gpu_capability()
    flags = get_llama_build_flags(cpuinfo_path=cpuinfo_path)
    profile_id = match_platform_profile(cpuinfo_path=cpuinfo_path)

    print("====================================================")
    print(" ⚡ vllm_serv 하드웨어 감지 및 llama.cpp 빌드 리포트")
    print("====================================================")
    print(f" 매칭 플랫폼 프로필 : {profile_id}")
    print(f" CPU 모델명       : {cpu_info.model_name}")
    print(f" CPU 아키텍처     : {cpu_info.architecture}")
    print(f" CPU 폴백 모드   : {'예 (보수적 옵션 적용)' if cpu_info.is_fallback else '아니오 (정상 감지)'}")
    print(f" SIMD 지원 현황   : SSE4.2={'✓' if cpu_info.supports_sse4_2 else '✗'}, AVX={'✓' if cpu_info.supports_avx else '✗'}, AVX2={'✓' if cpu_info.supports_avx2 else '✗'}, F16C={'✓' if cpu_info.supports_f16c else '✗'}, FMA={'✓' if cpu_info.supports_fma else '✗'}")
    print("----------------------------------------------------")
    print(f" GPU 모델명       : {gpu_info.gpu_name}")
    print(f" Compute Cap      : {gpu_info.compute_capability} (arch_code: sm_{gpu_info.cuda_arch_code})")
    print(f" VRAM 용량       : {gpu_info.total_vram_mb} MB")
    print("----------------------------------------------------")
    print(f" 생성된 CMake 인자: {flags.cmake_args_str}")
    print("====================================================")


def main():
    parser = argparse.ArgumentParser(description="CPU and GPU Hardware Capability Detector for llama.cpp Build")
    parser.add_argument("--format", choices=["report", "cmake", "json"], default="report", help="Output format (report, cmake, json)")
    parser.add_argument("--report", action="store_true", help="Print human-readable report (alias for --format report)")
    parser.add_argument("--match-profile", action="store_true", help="Print matched platform profile ID")
    parser.add_argument("--check-preflight", action="store_true", help="Run hardware acceleration pre-flight check")
    args = parser.parse_args()

    if args.match_profile:
        print(match_platform_profile())
        sys.exit(0)

    if args.check_preflight:
        preflight = check_hardware_preflight()
        if preflight["passed"]:
            print("[INFO] Hardware pre-flight check passed.")
            sys.exit(0)
        else:
            sys.stderr.write(f"{preflight['error_message']}\n")
            sys.exit(1)

    if args.report:
        args.format = "report"

    if args.format == "cmake":
        try:
            flags = get_llama_build_flags()
            print(flags.cmake_args_str)
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.exit(1)
    elif args.format == "json":
        try:
            cpu_info = detect_cpu_features()
            gpu_info = detect_gpu_capability()
            flags = get_llama_build_flags()
            profile_id = match_platform_profile()
            import json
            data = {
                "profile_id": profile_id,
                "cpu": cpu_info.model_dump(),
                "gpu": gpu_info.model_dump(),
                "build_flags": flags.model_dump()
            }
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.exit(1)
    else:
        try:
            print_detection_report()
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.exit(1)


if __name__ == "__main__":
    main()

