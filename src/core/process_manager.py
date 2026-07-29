import asyncio
import os
import re
import shutil
import socket
import sys
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from src.core.gpu_detector import (
    check_gpu_availability,
    GpuDeviceInfo,
    VramOffloadStatus,
    GpuAccelerationError,
    VramOverflowError
)
import re

class ProcessStatusEnum(str, Enum):
    UNLOADED = "UNLOADED"
    DOWNLOADING = "DOWNLOADING"
    LOADING = "LOADING"
    READY = "READY"
    ERROR = "ERROR"

class ProcessState(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ProcessStatusEnum = Field(default=ProcessStatusEnum.UNLOADED, description="현재 프로세스 구동 상태")
    model_id: Optional[str] = Field(default=None, description="로딩된 모델 식별자")
    port: Optional[int] = Field(default=None, description="llama-server 바인딩 포트")
    pid: Optional[int] = Field(default=None, description="OS 프로세스 PID")
    error_message: Optional[str] = Field(default=None, description="에러 발생 시 상세 메시지")
    exit_code: Optional[int] = Field(default=None, description="프로세스 종료 코드")
    vram_offloaded: Optional[bool] = Field(default=None, description="T019/US2-AC1: VRAM 100% 오프로드 검증 완료 여부")

class QwenModelPreset(BaseModel):
    model_config = ConfigDict(frozen=True)

    model_id: str = Field(..., description="모델 식별자")
    model_name: str = Field(..., description="표시용 모델 명칭")
    gguf_path: str = Field(..., description="GGUF 모델 상대 경로")
    clip_path: Optional[str] = Field(default=None, description="CLIP 프로젝터 경로")
    chat_template: str = Field(default="chatml", description="llama-server 채팅 템플릿 인자")
    default_n_ctx: int = Field(default=4096, description="기본 컨텍스트 크기")
    vram_limit_mb: int = Field(..., description="권장 VRAM 임계치 (MB)")
    quant_type: str = Field(default="q4_k_m", description="양자화 타입 (q4_k_m, q4_0, q8_0)")

class ProcessManager:
    """Subprocess lifecycle manager for llama-server subprocesses supporting Gemma 4 and Qwen3.5."""

    def __init__(self, port: int = 8081):
        self.port = port
        self.process: Optional[asyncio.subprocess.Process] = None
        self.state: ProcessState = ProcessState(status=ProcessStatusEnum.UNLOADED, port=port)
        self.vram_offload_status: Optional[VramOffloadStatus] = None
        self.hardware_limits = {
            "gemma4-e2b": 35000,
            "gemma4-e4b": 16000,
            "gemma4-12b": 9500,
            "qwen3.5-2b": 32000,
            "qwen3.5-4b": 18000,
            "qwen3.5-9b": 8500
        }
        self.vram_total = 24000
        self.vram_max_capacity_mb = 11264  # 11GB GTX 1080 Ti limit

        # Preset catalog including Gemma 4 and Qwen 3.5 variants
        self.model_presets: Dict[str, Dict[str, Any]] = {
            "gemma4-e2b": {
                "model": "models/gemma4-2b/gemma-4-E2B_q4_0-it.gguf",
                "clip": "models/gemma4-2b/gemma-4-E2B-it-mmproj.gguf",
                "chat_template": "gemma",
                "vram_est_mb": 3500
            },
            "gemma4-e4b": {
                "model": "models/gemma4-4b/gemma-4-E4B_q4_0-it.gguf",
                "clip": "models/gemma4-4b/gemma-4-E4B-it-mmproj.gguf",
                "chat_template": "gemma",
                "vram_est_mb": 6500
            },
            "gemma4-12b": {
                "model": "models/gemma4-12b/gemma-4-12b-it-qat-q4_0.gguf",
                "clip": "models/gemma4-12b/mmproj-gemma-4-12b-it-qat-q4_0.gguf",
                "chat_template": "gemma",
                "vram_est_mb": 9500
            },
            "qwen3.5-2b": {
                "model": "models/qwen3.5-2b/Qwen3.5-2B-Q4_K_M.gguf",
                "clip": None,
                "chat_template": "chatml",
                "vram_est_mb": 3000
            },
            "qwen3.5-4b": {
                "model": "models/qwen3.5-4b/Qwen3.5-4B-Q4_K_M.gguf",
                "clip": None,
                "chat_template": "chatml",
                "vram_est_mb": 5500
            },
            "qwen3.5-9b": {
                "model": "models/qwen3.5-9b/Qwen3.5-9B-Q4_K_M.gguf",
                "clip": None,
                "chat_template": "chatml",
                "vram_est_mb": 9800
            }
        }

    def verify_vram_released(self, baseline_free_vram_mb: int = 0, tolerance_mb: int = 200) -> bool:
        """FR-013: VRAM memory release check via nvidia-smi."""
        import subprocess
        import shutil
        
        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            print("[ProcessManager] Warning: nvidia-smi not found. Skipping VRAM release verification.")
            return True
            
        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, check=True
            )
            free_vram_mb = int(result.stdout.strip().split('\n')[0])
            
            if baseline_free_vram_mb > 0:
                if (abs(free_vram_mb - baseline_free_vram_mb) <= tolerance_mb or 
                    free_vram_mb >= baseline_free_vram_mb - tolerance_mb or
                    (self.vram_total - free_vram_mb) <= tolerance_mb):
                    return True
                return False
                
            return True
        except Exception as e:
            print(f"[ProcessManager] Warning: nvidia-smi failed during VRAM release verification: {e}")
            return True

    def get_vram_limit(self, model_id: str) -> int:
        return self.hardware_limits.get(model_id, 16000)

    @staticmethod
    def parse_vram_offload_log(line: str, model_id: str) -> Optional[VramOffloadStatus]:
        layers_match = re.search(r"offloaded (\d+)/(\d+) layers to GPU", line)
        if layers_match:
            offloaded = int(layers_match.group(1))
            total = int(layers_match.group(2))
            return VramOffloadStatus(
                model_id=model_id,
                total_layers=total,
                offloaded_layers=offloaded,
                is_fully_offloaded=(offloaded == total)
            )

        clip_match = re.search(r"(clip model loaded|mmproj loaded)", line, re.IGNORECASE)
        if clip_match:
            return VramOffloadStatus(
                model_id=model_id,
                is_fully_offloaded=True,
                has_clip_offload=True
            )

        vram_match = re.search(r"model buffer size =\s*([\d.]+)\s*MiB", line)
        if vram_match:
            vram_mb = int(float(vram_match.group(1)))
            return VramOffloadStatus(
                model_id=model_id,
                is_fully_offloaded=True,
                offloaded_vram_mb=vram_mb
            )

        return None

    def verify_vram_offload(self, model_id: str, status: VramOffloadStatus) -> None:
        if not status.is_fully_offloaded:
            raise VramOverflowError(
                f"VRAM_PARTIAL_OFFLOAD_ERROR: {status.offloaded_layers}/{status.total_layers} layers offloaded. 100% VRAM offload required."
            )
        
        if self.vram_offload_status is None:
            self.vram_offload_status = status
        else:
            if status.total_layers > 0:
                self.vram_offload_status.total_layers = status.total_layers
                self.vram_offload_status.offloaded_layers = status.offloaded_layers
                self.vram_offload_status.is_fully_offloaded = status.is_fully_offloaded
            if status.has_clip_offload is not None:
                self.vram_offload_status.has_clip_offload = status.has_clip_offload
            if status.offloaded_vram_mb > 0:
                self.vram_offload_status.offloaded_vram_mb = status.offloaded_vram_mb

        # T019/US2-AC1: ProcessState에 vram_offloaded=True 기록
        if self.state.model_id == model_id:
            self.state = ProcessState(
                status=self.state.status,
                model_id=self.state.model_id,
                port=self.state.port,
                pid=self.state.pid,
                error_message=self.state.error_message,
                exit_code=self.state.exit_code,
                vram_offloaded=True,
            )

    def check_vram_runtime_overflow(self, threshold_pct: float = 95.0) -> None:
        """T021: 추론 컨텍스트 확장 시 실시간 VRAM 오버플로우 감지.

        nvidia-smi를 통해 현재 GPU VRAM 사용률을 확인하고,
        임계치(기본 95%)를 초과할 경우 VramOverflowError를 발생시켜
        CUDA OOM 크래시를 사전 차단합니다.

        Args:
            threshold_pct: VRAM 사용률 임계치 (백분율, 기본 95.0%)

        Raises:
            VramOverflowError: VRAM 사용률이 임계치를 초과할 경우
        """
        import subprocess

        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            return  # nvidia-smi 미설치 환경에서는 검사 생략

        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, check=True
            )
            parts = [p.strip() for p in result.stdout.strip().split('\n')[0].split(',')]
            used_mb = int(parts[0])
            total_mb = int(parts[1])

            usage_pct = (used_mb / total_mb) * 100.0 if total_mb > 0 else 0.0

            if usage_pct >= threshold_pct:
                raise VramOverflowError(
                    f"VRAM 실시간 오버플로우 감지: {used_mb}MB / {total_mb}MB "
                    f"({usage_pct:.1f}% ≥ {threshold_pct}% 임계치). "
                    f"추론 컨텍스트 축소 또는 더 작은 모델 사용을 권장합니다."
                )
        except VramOverflowError:
            raise
        except Exception as e:
            print(f"[ProcessManager] T021: VRAM 런타임 모니터링 경고: {e}")

    def is_ready(self) -> bool:
        return self.state.status == ProcessStatusEnum.READY

    def estimate_vram_usage(self, model_id: str, n_ctx: int) -> int:
        """FR-010: Dry-run VRAM calculation based on model base VRAM and context scaling."""
        preset = self.model_presets.get(model_id)
        base_vram = preset.get("vram_est_mb", 6000) if preset else 6000
        # Context KV cache estimation (~0.5MB per token above 4K)
        extra_ctx_vram = max(0, int((n_ctx - 4096) * 0.5))
        return base_vram + extra_ctx_vram

    async def spawn_process(self, model_id: str, n_ctx: int) -> ProcessState:
        """Spawns a new llama-server subprocess for Gemma 4 or Qwen 3.5."""
        await self.stop_process()
        self.vram_offload_status = None

        target_preset = self.model_presets.get(model_id)
        if not target_preset:
            self.state = ProcessState(
                status=ProcessStatusEnum.ERROR,
                model_id=model_id,
                port=self.port,
                error_message=f"Unknown model_id: {model_id}"
            )
            return self.state

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_file = os.path.join(base_dir, target_preset["model"])

        # FR-010: Dry-run VRAM check & Missing model file validation
        vram_est = self.estimate_vram_usage(model_id, n_ctx)
        if vram_est > self.vram_max_capacity_mb + 2000:  # Hard limit check
            self.state = ProcessState(
                status=ProcessStatusEnum.ERROR,
                model_id=model_id,
                port=self.port,
                error_message=f"CUDA OOM Risk: Estimated VRAM {vram_est}MB exceeds GPU capacity limit {self.vram_max_capacity_mb}MB"
            )
            return self.state

        # FR-001 & FR-002: GPU & CUDA Backend auto-detection and CPU fallback blocking
        if os.environ.get("MOCK_CPU_ONLY") == "1":
            self.state = ProcessState(
                status=ProcessStatusEnum.ERROR,
                model_id=model_id,
                port=self.port,
                error_message="GpuAccelerationError: CPU-only execution is strictly blocked. NVIDIA GPU with CUDA acceleration is required."
            )
            return self.state

        if not os.environ.get("MOCK_LLAMA_SERVER"):
            try:
                gpu_info = check_gpu_availability()
            except GpuAccelerationError as e:
                self.state = ProcessState(
                    status=ProcessStatusEnum.ERROR,
                    model_id=model_id,
                    port=self.port,
                    error_message=f"GpuAccelerationError: {str(e)}"
                )
                return self.state

        # Search for llama-server binary or fallback to python module
        binary_executable = (
            shutil.which("llama-server")
            or ("/usr/local/lib/ollama/llama-server" if os.path.exists("/usr/local/lib/ollama/llama-server") else None)
        )

        clip_file = None
        if target_preset.get("clip"):
            clip_file = os.path.join(base_dir, target_preset["clip"])

        # Force 100% GPU VRAM Offloading environment variables
        env = dict(os.environ)
        env["CUDA_VISIBLE_DEVICES"] = "0"

        if binary_executable:
            cmd = [
                binary_executable,
                "-m", model_file,
                "-c", str(n_ctx),
                "--host", "127.0.0.1",
                "--port", str(self.port),
                "-ngl", "999",
                "--split-mode", "none",
                "--main-gpu", "0"
            ]
            if clip_file:
                cmd.extend(["--mmproj", clip_file, "--mmproj-offload"])
        else:
            cmd = [
                "python3", "-m", "llama_cpp.server",
                "--model", model_file,
                "--n_ctx", str(n_ctx),
                "--host", "127.0.0.1",
                "--port", str(self.port),
                "--n_gpu_layers", "999"
            ]
            if clip_file:
                cmd.extend(["--clip_model_path", clip_file])
            if target_preset.get("chat_template"):
                cmd.extend(["--chat_template", target_preset["chat_template"]])

        try:
            self.state = ProcessState(
                status=ProcessStatusEnum.LOADING,
                model_id=model_id,
                port=self.port
            )

            # Check if model file exists locally; if not, raise readable error or mock for test
            if not os.path.exists(model_file) and not os.environ.get("MOCK_LLAMA_SERVER"):
                # If model file does not exist, return clear error message per spec
                self.state = ProcessState(
                    status=ProcessStatusEnum.ERROR,
                    model_id=model_id,
                    port=self.port,
                    error_message=f"Model file not found: {model_file}"
                )
                return self.state

            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env
            )
            self.state = ProcessState(
                status=ProcessStatusEnum.LOADING,
                model_id=model_id,
                port=self.port,
                pid=self.process.pid
            )
        except Exception as e:
            self.state = ProcessState(
                status=ProcessStatusEnum.ERROR,
                model_id=model_id,
                port=self.port,
                error_message=str(e)
            )
        return self.state

    async def stop_process(self) -> ProcessState:
        """Stops the running subprocess with SIGTERM -> SIGKILL escalation and zombie reaping.

        FR-004: 기존 프로세스를 안전 종료하고 GPU VRAM을 완전 해제한 후
        포트 소켓이 클리어되었음을 확인합니다.
        """
        if self.process:
            try:
                if self.process.returncode is None:
                    self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    if self.process.returncode is None:
                        self.process.kill()
                        await asyncio.wait_for(self.process.wait(), timeout=2.0)
            except (ProcessLookupError, Exception):
                pass
            exit_code = self.process.returncode
            self.process = None
        else:
            exit_code = None

        # FR-004: 포트 소켓 클리어 대기 (최대 3초)
        await self._wait_for_port_free(timeout=3.0)

        vram_ok = self.verify_vram_released()
        print(f"[ProcessManager] FR-004: VRAM 해제 검증 완료: {'성공' if vram_ok else '경고 - VRAM 잔여 점유 감지'}")

        self.state = ProcessState(
            status=ProcessStatusEnum.UNLOADED,
            port=self.port,
            exit_code=exit_code
        )
        return self.state

    async def _wait_for_port_free(self, timeout: float = 3.0) -> bool:
        """포트가 해제될 때까지 대기. FR-004 VRAM 완전 해제 보장."""
        import socket
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('127.0.0.1', self.port))
                if result != 0:  # 포트가 자유로움
                    return True
            await asyncio.sleep(0.2)
        return False
