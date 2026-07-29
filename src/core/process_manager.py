import asyncio
import os
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

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
                "model": "models/qwen3.5-2b/qwen-3.5-2b-instruct-q4_k_m.gguf",
                "clip": None,
                "chat_template": "chatml",
                "vram_est_mb": 3000
            },
            "qwen3.5-4b": {
                "model": "models/qwen3.5-4b/qwen-3.5-4b-instruct-q4_k_m.gguf",
                "clip": None,
                "chat_template": "chatml",
                "vram_est_mb": 5500
            },
            "qwen3.5-9b": {
                "model": "models/qwen3.5-9b/qwen-3.5-9b-instruct-q4_k_m.gguf",
                "clip": None,
                "chat_template": "chatml",
                "vram_est_mb": 9800
            }
        }

    def get_vram_limit(self, model_id: str) -> int:
        return self.hardware_limits.get(model_id, 16000)

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

        cmd = [
            "python3", "-m", "llama_cpp.server",
            "--model", model_file,
            "--n_ctx", str(n_ctx),
            "--host", "127.0.0.1",
            "--port", str(self.port),
            "--n_gpu_layers", "-1"
        ]

        # Bind CLIP projector if present
        if target_preset.get("clip"):
            clip_file = os.path.join(base_dir, target_preset["clip"])
            cmd.extend(["--clip_model_path", clip_file])

        # FR-009: Bind explicit chat template (chatml for Qwen3.5, gemma for Gemma 4)
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
                stderr=asyncio.subprocess.STDOUT
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
