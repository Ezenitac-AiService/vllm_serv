"""
GPU and CUDA Acceleration Detector and Exception Hierarchy.
Provides hardware validation, VRAM memory checks, and CUDA backend verification.
"""

import re
import subprocess
import shutil
from typing import Optional
from pydantic import BaseModel, Field


class GpuValidationError(Exception):
    """Base exception for GPU validation errors."""
    pass


class GpuAccelerationError(GpuValidationError):
    """Raised when GPU is not detected, CUDA backend is unavailable, or CPU-only binary is executed."""
    pass


class VramOverflowError(GpuValidationError):
    """Raised when VRAM is insufficient or model layers fail to 100% offload to GPU VRAM."""
    pass


class PortCollisionError(GpuValidationError):
    """Raised when port 8081 is occupied by zombie or colliding process."""
    pass


class GpuDeviceInfo(BaseModel):
    """GPU Device and CUDA Runtime Information."""
    device_id: int = Field(default=0, description="GPU device index")
    name: str = Field(default="NVIDIA GPU", description="GPU device model name")
    total_vram_mb: int = Field(default=0, description="Total VRAM capacity in MB")
    free_vram_mb: int = Field(default=0, description="Currently available VRAM in MB")
    driver_version: Optional[str] = Field(default=None, description="NVIDIA Driver version")
    cuda_version: Optional[str] = Field(default=None, description="CUDA Runtime version")
    is_cuda_available: bool = Field(default=False, description="Whether CUDA GPU acceleration is available")


class VramOffloadStatus(BaseModel):
    """VRAM Offload Verification Status."""
    model_id: str = Field(..., description="Model identifier")
    total_layers: int = Field(default=0, description="Total transformer layers")
    offloaded_layers: int = Field(default=0, description="Layers offloaded to GPU VRAM")
    is_fully_offloaded: bool = Field(default=False, description="True if 100% of layers offloaded to VRAM")
    offloaded_vram_mb: int = Field(default=0, description="VRAM footprint in MB")
    has_clip_offload: Optional[bool] = Field(default=None, description="Multimodal CLIP projector offloaded")


def check_gpu_availability() -> GpuDeviceInfo:
    """
    Scans system for NVIDIA GPU and verifies CUDA hardware acceleration backend.

    Raises:
        GpuAccelerationError: If no NVIDIA GPU is detected or CUDA backend is unavailable.
    """
    nvidia_smi_path = shutil.which("nvidia-smi")
    if not nvidia_smi_path:
        raise GpuAccelerationError(
            "NVIDIA GPU driver / nvidia-smi tool not found. GPU acceleration is required."
        )

    try:
        # Run nvidia-smi query to get GPU details
        cmd = [
            nvidia_smi_path,
            "--query-gpu=name,memory.total,memory.free,driver_version",
            "--format=csv,noheader,nounits"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        if not lines or not lines[0]:
            raise GpuAccelerationError("No active NVIDIA GPU detected by nvidia-smi.")

        parts = [p.strip() for p in lines[0].split(",")]
        gpu_name = parts[0] if len(parts) > 0 else "NVIDIA GPU"
        total_vram = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 11264
        free_vram = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 8500
        driver_ver = parts[3] if len(parts) > 3 else "Unknown"

        # T018: nvidia-smi 일반 출력에서 CUDA 버전 동적 감지
        detected_cuda_version: Optional[str] = None
        try:
            smi_res = subprocess.run(
                [nvidia_smi_path], capture_output=True, text=True, check=True
            )
            cuda_match = re.search(r'CUDA Version:\s*([\d.]+)', smi_res.stdout)
            if cuda_match:
                detected_cuda_version = cuda_match.group(1)
        except (subprocess.CalledProcessError, OSError):
            pass

        # T020: nvcc (CUDA toolkit compiler) 버전 감지
        nvcc_version: Optional[str] = None
        nvcc_path = shutil.which("nvcc")
        if nvcc_path:
            try:
                nvcc_res = subprocess.run(
                    [nvcc_path, "--version"], capture_output=True, text=True, check=True
                )
                nvcc_match = re.search(r'release\s+([\d.]+)', nvcc_res.stdout)
                if nvcc_match:
                    nvcc_version = nvcc_match.group(1)
            except (subprocess.CalledProcessError, OSError):
                pass

        # Check llama_cpp CUDA support (compatible with both old and new API)
        is_cuda_supported = True
        try:
            import llama_cpp
            if hasattr(llama_cpp, 'llama_supports_gpu_offload'):
                is_cuda_supported = llama_cpp.llama_supports_gpu_offload()
            elif hasattr(llama_cpp, 'llama_supports_gpu'):
                is_cuda_supported = llama_cpp.llama_supports_gpu()
        except ImportError:
            pass

        if not is_cuda_supported:
            # T020: CUDA 가속 미지원 시 문제 해결 안내 메시지 구성
            troubleshoot_lines = [
                "설치된 llama-cpp-python에 CUDA 가속 지원이 없습니다.",
                "문제 해결 방법:",
                "  1. llama-cpp-python이 CUDA 지원으로 빌드되었는지 확인하세요.",
                "  2. nvidia-smi와 nvcc 버전 호환성을 확인하세요.",
                f"     - nvidia-smi CUDA Version: {detected_cuda_version or 'N/A'}",
                f"     - nvcc version: {nvcc_version or 'N/A'}",
                "  3. CUDA cmake 인수를 사용하여 재설치하세요:",
                '     pip install llama-cpp-python --force-reinstall --no-cache-dir'
            ]
            if not nvcc_path:
                troubleshoot_lines.append(
                    "  [경고] nvcc (CUDA toolkit compiler)를 찾을 수 없습니다. CUDA toolkit이 설치되어 있는지 확인하세요."
                )
            raise GpuAccelerationError("\n".join(troubleshoot_lines))

        return GpuDeviceInfo(
            device_id=0,
            name=gpu_name,
            total_vram_mb=total_vram,
            free_vram_mb=free_vram,
            driver_version=driver_ver,
            cuda_version=detected_cuda_version,
            is_cuda_available=True
        )

    except subprocess.CalledProcessError as e:
        raise GpuAccelerationError(f"nvidia-smi command failed: {e}")
    except Exception as e:
        if isinstance(e, GpuAccelerationError):
            raise e
        raise GpuAccelerationError(f"Failed to verify GPU hardware: {str(e)}")


def get_nvml_vram_info(device_index: int = 0) -> GpuDeviceInfo:
    """FR-008: Non-blocking VRAM inspection via PyNVML C-API (<1ms), with nvidia-smi fallback."""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(name, bytes):
            name = name.decode("utf-8")
        total_mb = int(info.total / (1024 * 1024))
        free_mb = int(info.free / (1024 * 1024))
        pynvml.nvmlShutdown()
        return GpuDeviceInfo(
            device_id=device_index,
            name=name,
            total_vram_mb=total_mb,
            free_vram_mb=free_mb,
            is_cuda_available=True
        )
    except Exception:
        # Fallback to nvidia-smi
        return check_gpu_availability()


def get_realtime_usable_vram(safety_margin_mb: Optional[int] = None, n_ctx: int = 4096) -> int:
    """T003 / FR-001: Returns real-time usable VRAM in MB calculated from NVML free VRAM minus dynamic safety margin (500 + n_ctx * 0.05)."""
    try:
        if safety_margin_mb is None:
            safety_margin_mb = 500 + int(n_ctx * 0.05)
        gpu_info = get_nvml_vram_info()
        return max(0, gpu_info.free_vram_mb - safety_margin_mb)
    except Exception:
        return 0


def wait_for_nvml_vram_settled(
    poll_interval: float = 0.2,
    max_attempts: int = 5,
    delta_threshold_mb: int = 10
) -> GpuDeviceInfo:
    """T004 / DoD-004: Polls NVML Free VRAM until consecutive reads differ by < delta_threshold_mb."""
    import time
    prev_info = get_nvml_vram_info()
    for _ in range(max_attempts - 1):
        time.sleep(poll_interval)
        curr_info = get_nvml_vram_info()
        if abs(curr_info.free_vram_mb - prev_info.free_vram_mb) < delta_threshold_mb:
            return curr_info
        prev_info = curr_info
    return prev_info


def estimate_kv_cache_vram(
    n_layers: int = 36,
    n_heads: int = 32,
    head_dim: int = 128,
    n_ctx: int = 4096,
    bytes_per_element: int = 2
) -> int:
    """FR-012: Pre-flight KV Cache VRAM estimator (2 * L * H * D * n_ctx * bytes). Returns VRAM MB."""
    # 2 for Key and Value matrices
    total_bytes = 2 * n_layers * n_heads * head_dim * n_ctx * bytes_per_element
    return max(1, int(total_bytes / (1024 * 1024)))


def calculate_max_allocatable_n_ctx(
    usable_kv_budget_mb: int,
    n_layers: int = 36,
    n_heads: int = 32,
    head_dim: int = 128,
    bytes_per_element: int = 2,
    step: int = 512,
    max_cap: int = 131072
) -> int:
    """T008 / FR-002: Calculates the maximum allocatable n_ctx (aligned to step) fitting within usable_kv_budget_mb."""
    if usable_kv_budget_mb <= 0:
        return 2048

    bytes_per_ctx_token = 2 * n_layers * n_heads * head_dim * bytes_per_element
    max_bytes = usable_kv_budget_mb * 1024 * 1024
    raw_n_ctx = int(max_bytes / bytes_per_ctx_token) if bytes_per_ctx_token > 0 else 2048

    aligned_n_ctx = (raw_n_ctx // step) * step
    aligned_n_ctx = min(max_cap, max(2048, aligned_n_ctx))
    return aligned_n_ctx


def validate_cuda_build_environment() -> bool:
    """FR-005: Fail-fast CUDA build environment validation.

    Validates that both nvcc (CUDA Toolkit compiler) and nvidia-smi (GPU driver)
    are present on the system. Raises GpuAccelerationError if either is missing,
    strictly blocking CPU-only fallback.

    Returns:
        True if both nvcc and nvidia-smi are available.

    Raises:
        GpuAccelerationError: If nvcc or nvidia-smi is not found.
    """
    nvidia_smi_path = shutil.which("nvidia-smi")
    if not nvidia_smi_path:
        raise GpuAccelerationError(
            "NVIDIA GPU 드라이버(nvidia-smi)가 감지되지 않았습니다.\n"
            "NVIDIA GPU 가속 서빙을 위해 GPU 드라이버 설치가 필수입니다.\n"
            "CPU 전용 폴백은 허용되지 않습니다."
        )

    nvcc_path = shutil.which("nvcc")
    if not nvcc_path:
        raise GpuAccelerationError(
            "NVIDIA CUDA Toolkit (nvcc)가 감지되지 않았습니다.\n"
            "llama-cpp-python CUDA 가속 빌드를 위해 nvcc 설치가 필수입니다.\n"
            "설치: sudo apt install nvidia-cuda-toolkit 또는 https://developer.nvidia.com/cuda-downloads\n"
            "CPU 전용 폴백은 허용되지 않습니다."
        )

    # Verify llama_cpp GPU support if available
    try:
        import llama_cpp
        # Compatible with both old (llama_supports_gpu) and new (llama_supports_gpu_offload) API
        gpu_check_fn = getattr(llama_cpp, 'llama_supports_gpu_offload', None) or getattr(llama_cpp, 'llama_supports_gpu', None)
        if gpu_check_fn is not None:
            if not gpu_check_fn():
                raise GpuAccelerationError(
                    "llama-cpp-python이 CPU 전용 모드로 설치되어 있습니다.\n"
                    "CUDA 가속 빌드로 재설치가 필요합니다:\n"
                    '  CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python --no-binary llama-cpp-python --force-reinstall'
                )
    except ImportError:
        pass  # llama_cpp not yet installed; will be built with CUDA

    return True

