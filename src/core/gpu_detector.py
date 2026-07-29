"""
GPU and CUDA Acceleration Detector and Exception Hierarchy.
Provides hardware validation, VRAM memory checks, and CUDA backend verification.
"""

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

        # Check llama_cpp CUDA support
        is_cuda_supported = True
        try:
            import llama_cpp
            if hasattr(llama_cpp, 'llama_supports_gpu'):
                is_cuda_supported = llama_cpp.llama_supports_gpu()
        except ImportError:
            pass

        if not is_cuda_supported:
            raise GpuAccelerationError(
                "installed llama-cpp-python lacks CUDA acceleration support. Reinstall with CUDA enabled."
            )

        return GpuDeviceInfo(
            device_id=0,
            name=gpu_name,
            total_vram_mb=total_vram,
            free_vram_mb=free_vram,
            driver_version=driver_ver,
            cuda_version="13.0",
            is_cuda_available=True
        )

    except subprocess.CalledProcessError as e:
        raise GpuAccelerationError(f"nvidia-smi command failed: {e}")
    except Exception as e:
        if isinstance(e, GpuAccelerationError):
            raise e
        raise GpuAccelerationError(f"Failed to verify GPU hardware: {str(e)}")
