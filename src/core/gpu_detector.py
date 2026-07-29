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

        # Check llama_cpp CUDA support
        is_cuda_supported = True
        try:
            import llama_cpp
            if hasattr(llama_cpp, 'llama_supports_gpu'):
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

