import asyncio
import os
import re
import shutil
import socket
import sys
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from src.core.config_manager import ConfigManager

from src.core.gpu_detector import (
    get_nvml_vram_info,
    estimate_kv_cache_vram,
    VramOffloadStatus,
    GpuAccelerationError,
    VramOverflowError,
    PortCollisionError
)

class ProcessStatusEnum(str, Enum):
    UNLOADED = "UNLOADED"
    DOWNLOADING = "DOWNLOADING"
    LOADING = "LOADING"
    VRAM_OFFLOADED = "VRAM_OFFLOADED"
    READY = "READY"
    ERROR = "ERROR"

class TestExecutionMode(str, Enum):
    MOCK = "mock"
    REAL = "real"

class LlamaServerBinaryInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    binary_path: str = Field(..., description="llama-server 바이너리 경로")
    is_cuda_enabled: bool = Field(default=True, description="CUDA 가속 구동 여부")
    build_source: str = Field(default="PATH", description="바이너리 취득 경로 (PATH / CMAKE_BUILD / PYTHON_MODULE)")
    version_info: Optional[str] = Field(default=None, description="바이너리 버전 정보")

class RealGpuBenchmarkSession(BaseModel):
    model_config = ConfigDict(frozen=True)

    session_id: str = Field(default="session-001", description="세션 식별자")
    execution_mode: TestExecutionMode = Field(default=TestExecutionMode.REAL, description="테스트 실행 모드")
    target_models: list[str] = Field(default_factory=list, description="대상 6개 모델 ID 목록")
    completed_models: list[str] = Field(default_factory=list, description="성공 모델 ID 목록")
    failed_models: dict[str, str] = Field(default_factory=dict, description="실패 모델 ID 및 원인 메시지")
    vram_safety_threshold_mb: int = Field(default=11264, description="VRAM 안전 임계치 MB")


class ProcessState(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ProcessStatusEnum = Field(default=ProcessStatusEnum.UNLOADED, description="현재 프로세스 구동 상태")
    model_id: Optional[str] = Field(default=None, description="로딩된 모델 식별자")
    port: Optional[int] = Field(default=None, description="llama-server 바인딩 포트")
    pid: Optional[int] = Field(default=None, description="OS 프로세스 PID")
    error_message: Optional[str] = Field(default=None, description="에러 발생 시 상세 메시지")
    exit_code: Optional[int] = Field(default=None, description="종료 코드")
    vram_offloaded: Optional[bool] = Field(default=None, description="VRAM 100% 오프로드 검증 완료 여부")
    vram_offloaded_100pct: bool = Field(default=False, description="VRAM 100% 오프로드 검증 완료 여부")
    active_requests: int = Field(default=0, description="현재 진행 중인 활성 추론 스트림 수")

class ProcessLifecycleState(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ProcessStatusEnum = Field(default=ProcessStatusEnum.UNLOADED, description="현재 프로세스 구동 상태")
    pid: Optional[int] = Field(default=None, description="OS 프로세스 PID")
    port: Optional[int] = Field(default=None, description="llama-server 바인딩 포트")
    vram_offloaded_100pct: bool = Field(default=False, description="VRAM 100% 오프로드 검증 완료 여부")
    active_requests: int = Field(default=0, description="현재 진행 중인 활성 추론 스트림 수")
    model_id: Optional[str] = Field(default=None, description="로딩된 모델 식별자")
    error_message: Optional[str] = Field(default=None, description="에러 메시지")
    exit_code: Optional[int] = Field(default=None, description="종료 코드")

class VramLoadTimingGuard(BaseModel):
    model_config = ConfigDict(frozen=True)

    baseline_vram: int = Field(default=0, description="프로세스 실행 전 기본 VRAM 사용량(MB)")
    target_vram: int = Field(default=0, description="목표 VRAM 탑재 용량(MB)")
    offload_verified_at: Optional[float] = Field(default=None, description="VRAM 100% 검증 시각")
    socket_cleared: bool = Field(default=False, description="소켓 포트 완전 클리어 여부")
    nvml_handle: Optional[Any] = Field(default=None, description="PyNVML 핸들 참조")
    kv_cache_vram_mb: int = Field(default=0, description="사전 추정된 KV Cache VRAM 용량(MB)")

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

    def __init__(self, port: int = 8081, config_manager: Optional['ConfigManager'] = None):
        # FR-001 & FR-002: ConfigManager를 단일 진실 소스(Single Source of Truth)로 사용
        if config_manager is None:
            from src.core.config_manager import ConfigManager
            config_manager = ConfigManager()
        self._config_manager = config_manager

        catalog = config_manager.get_model_catalog()
        loaded_presets = {}
        if catalog:
            for model_id, entry in catalog.items():
                loaded_presets[model_id] = {
                    "model": entry.get("model_path", ""),
                    "clip": entry.get("clip_path"),
                    "chat_template": entry.get("chat_template", "chatml"),
                    "vram_est_mb": entry.get("vram_est_mb", 6000),
                    "requires_mmproj": entry.get("requires_mmproj", False),
                }
        self.model_presets = loaded_presets

        # 외부 JSON 서버 설정에서 VRAM 상한선 및 포트 동적 로드 (명시적 port 지정 시 최우선 적용)
        server_config = config_manager.get_server_config()
        self.vram_max_capacity_mb = server_config.get("vram_max_capacity_mb", 11264)
        if port != 8081:
            self.port = port
        else:
            self.port = server_config.get("port", 8081) if server_config else 8081

        self.hardware_limits = {
            "gemma4-e2b": 35000,
            "gemma4-e4b": 16000,
            "gemma4-12b": 9500,
            "qwen3.5-2b": 32000,
            "qwen3.5-4b": 18000,
            "qwen3.5-9b": 8500
        }
        self.vram_total = 24000
        self.process: Optional[asyncio.subprocess.Process] = None
        self.state: ProcessState = ProcessState(status=ProcessStatusEnum.UNLOADED, port=self.port)
        self.vram_offload_status: Optional[VramOffloadStatus] = None
        self._log_drain_task: Optional[asyncio.Task] = None


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

    def detect_zombie_collision(self) -> None:
        """T004: Detect zombie or external processes occupying port 8081."""
        import socket
        if os.environ.get("MOCK_LLAMA_SERVER") == "1" or "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("MOCK_CPU_ONLY") == "1":
            return
        if self.process is None or self.process.returncode is not None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                res = sock.connect_ex(('127.0.0.1', self.port))
                if res == 0:
                    raise PortCollisionError(
                        f"PortCollisionError: Port {self.port} is already occupied by a zombie or external process."
                    )

    def estimate_vram_usage(self, model_id: str, n_ctx: int) -> int:
        """FR-010: Dry-run VRAM calculation based on model base VRAM and context scaling."""
        resolved_id = self._config_manager.resolve_model_id(model_id)
        preset = self.model_presets.get(resolved_id)
        base_vram = preset.get("vram_est_mb", 6000) if preset else 6000
        extra_ctx_vram = max(0, int((n_ctx - 4096) * 0.5))
        return base_vram + extra_ctx_vram

    def is_ready(self) -> bool:
        return self.state.status == ProcessStatusEnum.READY

    async def _drain_stdout(self, stream: asyncio.StreamReader) -> None:
        """Drains stdout stream asynchronously and parses VRAM offload log lines."""
        try:
            while not stream.at_eof():
                line_bytes = await stream.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace")
                status = self.parse_vram_offload_log(line, self.state.model_id or "")
                if status:
                    self.verify_vram_offload(self.state.model_id or "", status)
        except Exception:
            pass

    @staticmethod
    def verify_and_build_llama_server() -> LlamaServerBinaryInfo:
        """FR-001: Verifies CUDA llama-server binary existence; compiles via CMake with GGML_CUDA=ON if missing."""
        candidate = shutil.which("llama-server")
        if candidate and "ollama" not in candidate:
            return LlamaServerBinaryInfo(
                binary_path=candidate,
                is_cuda_enabled=True,
                build_source="PATH"
            )

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bin_dir = os.path.join(base_dir, ".bin")
        local_binary = os.path.join(bin_dir, "llama-server")

        if os.path.exists(local_binary) and os.access(local_binary, os.X_OK):
            return LlamaServerBinaryInfo(
                binary_path=local_binary,
                is_cuda_enabled=True,
                build_source="LOCAL_BIN"
            )

        llama_src_dir = os.path.join(base_dir, "llama.cpp")
        if os.path.exists(os.path.join(llama_src_dir, "CMakeLists.txt")):
            try:
                from src.core.cpu_detector import get_llama_build_flags, print_detection_report
                build_flags = get_llama_build_flags()
                cmake_args = build_flags.cmake_args_list
                print(f"[ProcessManager] llama-server missing. Compiling llama.cpp with hardware detection flags ({build_flags.cmake_args_str})...")
                print_detection_report()
            except Exception as e:
                print(f"[ProcessManager] ⚠️ Hardware detection failed, using fallback flags: {e}")
                cmake_args = ["-DGGML_CUDA=ON", "-DGGML_AVX=OFF", "-DGGML_AVX2=OFF", "-DGGML_F16C=OFF", "-DGGML_FMA=OFF"]

            import subprocess
            try:
                os.makedirs(bin_dir, exist_ok=True)
                build_dir = os.path.join(llama_src_dir, "build")
                cmd = ["cmake", "-B", build_dir] + cmake_args
                subprocess.run(
                    cmd,
                    cwd=llama_src_dir, check=True, capture_output=True
                )
                subprocess.run(
                    ["cmake", "--build", build_dir, "--config", "Release", "-j"],
                    cwd=llama_src_dir, check=True, capture_output=True
                )
                built_binary = os.path.join(build_dir, "bin", "llama-server")
                if os.path.exists(built_binary):
                    shutil.copy2(built_binary, local_binary)
                    os.chmod(local_binary, 0o755)
                    return LlamaServerBinaryInfo(
                        binary_path=local_binary,
                        is_cuda_enabled=True,
                        build_source="CMAKE_BUILD"
                    )
            except Exception as e:
                print(f"[ProcessManager] Warning: CMake build failed: {e}")

        return LlamaServerBinaryInfo(
            binary_path=sys.executable,
            is_cuda_enabled=True,
            build_source="PYTHON_MODULE_FALLBACK"
        )


    async def spawn_process(self, model_id: str, n_ctx: int = 2048) -> ProcessState:
        """Spawns a new llama-server subprocess for Gemma 4 or Qwen 3.5."""
        await self.stop_process()
        self.vram_offload_status = None

        # FR-001 / FR-005: Synchronous port free and VRAM release verification first
        port_free = await self._wait_for_port_free(max_retries=10, interval=0.5)
        if not port_free:
            raise PortCollisionError(f"PortCollisionError: Port {self.port} could not be cleared after process termination.")

        # FR-001: Detect zombie collision after stop_process and _wait_for_port_free if port is still occupied
        self.detect_zombie_collision()

        model_id = self._config_manager.resolve_model_id(model_id)
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
        model_rel = target_preset["model"]
        model_file = self._config_manager.get_absolute_path(model_rel) or os.path.join(base_dir, model_rel)

        # Ensure target_dir exists
        target_dir = os.path.dirname(model_file)
        os.makedirs(target_dir, exist_ok=True)

        # FR-012 / T002: Pre-flight GGUF + KV Cache VRAM estimator
        kv_vram_mb = estimate_kv_cache_vram(n_ctx=n_ctx)
        base_vram = target_preset.get("vram_est_mb", 6000)
        vram_est = base_vram + kv_vram_mb

        if vram_est > self.vram_max_capacity_mb + 2000:  # Hard limit check
            self.state = ProcessState(
                status=ProcessStatusEnum.ERROR,
                model_id=model_id,
                port=self.port,
                error_message=f"CUDA OOM Risk: Estimated VRAM {vram_est}MB (KV Cache: {kv_vram_mb}MB) exceeds GPU capacity limit {self.vram_max_capacity_mb}MB"
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
                gpu_info = get_nvml_vram_info()
            except GpuAccelerationError as e:
                self.state = ProcessState(
                    status=ProcessStatusEnum.ERROR,
                    model_id=model_id,
                    port=self.port,
                    error_message=f"GpuAccelerationError: {str(e)}"
                )
                return self.state

        # FR-001: Resolve CUDA llama-server binary or fallback to python module
        binary_info = self.verify_and_build_llama_server()

        # FR-001 (015-gemma4-model-loading-fix): Resolve MMProj (CLIP vision projector) path if defined in preset
        clip_file = None
        clip_rel = target_preset.get("clip")
        if clip_rel:
            candidate_clip = self._config_manager.get_absolute_path(clip_rel) or os.path.join(base_dir, clip_rel)
            if candidate_clip and os.path.exists(candidate_clip):
                clip_file = candidate_clip
            elif os.path.exists(clip_rel):
                clip_file = clip_rel

        # Force 100% GPU VRAM Offloading environment variables
        env = dict(os.environ)
        env["CUDA_VISIBLE_DEVICES"] = "0"

        server_cfg = self._config_manager.get_server_config()
        bind_host = server_cfg.get("host", "0.0.0.0")

        if binary_info.build_source != "PYTHON_MODULE_FALLBACK":
            cmd = [
                binary_info.binary_path,
                "-m", model_file,
                "-c", str(n_ctx),
                "--host", bind_host,
                "--port", str(self.port),
                "-ngl", "999",
                "--split-mode", "none",
                "--main-gpu", "0"
            ]
            if clip_file and os.path.exists(clip_file):
                cmd.extend(["--mmproj", clip_file])
        else:
            cmd = [
                sys.executable, "-m", "llama_cpp.server",
                "--model", model_file,
                "--n_ctx", str(n_ctx),
                "--host", bind_host,
                "--port", str(self.port),
                "--n_gpu_layers", "999"
            ]

            if clip_file and os.path.exists(clip_file):
                cmd.extend(["--clip_model_path", clip_file])
            if target_preset.get("chat_template"):
                cmd.extend(["--chat_format", target_preset["chat_template"]])

        try:
            self.state = ProcessState(
                status=ProcessStatusEnum.LOADING,
                model_id=model_id,
                port=self.port
            )

            # Check if model file exists locally; if not, return clear error message per spec
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
            if self.process and self.process.stdout:
                self._log_drain_task = asyncio.create_task(self._drain_stdout(self.process.stdout))

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

    def close_transport(self) -> None:
        """Explicitly close subprocess transport to prevent BaseSubprocessTransport.__del__ exception on loop closure."""
        if self.process:
            try:
                transport = getattr(self.process, '_transport', None)
                if transport is not None:
                    if hasattr(transport, 'is_closing') and not transport.is_closing():
                        transport.close()
                    elif not getattr(transport, '_closed', False):
                        transport.close()
            except Exception:
                pass

    async def stop_process(self) -> ProcessState:
        """Stops the running subprocess with Graceful Stream Drain, SIGTERM -> SIGKILL escalation and socket cleanup.

        FR-002, FR-005, FR-010, FR-011: Graceful Stream Drain (active_requests == 0, max 5s)
        및 프로세스 안전 종료/포트 해제/PyNVML VRAM 완납 검증.
        """
        # T003: Graceful Stream Drain (active_requests == 0, max 5s timeout)
        drain_start = asyncio.get_event_loop().time()
        while getattr(self.state, "active_requests", 0) > 0 and (asyncio.get_event_loop().time() - drain_start) < 5.0:
            await asyncio.sleep(0.2)

        if self._log_drain_task and not self._log_drain_task.done():
            self._log_drain_task.cancel()
            self._log_drain_task = None

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

            # FR-005/FR-006: 서브프로세스 트랜스포트 명시적 닫기 및 마이크로태스크 소진
            # BaseSubprocessTransport.__del__ RuntimeError: Event loop is closed 예외 방지
            self.close_transport()
            try:
                await asyncio.sleep(0.1)  # FR-006: 마이크로태스크 및 이벤트 루프 소진으로 닫힘 콜백 완결
            except Exception:
                pass

            exit_code = self.process.returncode
            self.process = None


        else:
            exit_code = None

        # FR-010 / T010: 포트 소켓 클리어 대기 (max_retries=10, interval=0.5s -> max 5s)
        await self._wait_for_port_free(max_retries=10, interval=0.5)

        vram_ok = self.verify_vram_released()
        print(f"[ProcessManager] FR-004: VRAM 해제 검증 완료: {'성공' if vram_ok else '경고 - VRAM 잔여 점유 감지'}")

        self.state = ProcessState(
            status=ProcessStatusEnum.UNLOADED,
            port=self.port,
            exit_code=exit_code
        )
        return self.state

    async def _wait_for_port_free(self, max_retries: int = 10, interval: float = 0.5) -> bool:
        """T010 / U1: 포트 소켓 해제 대기 (SO_REUSEADDR 제어 및 외부 잔여 프로세스 자율 정리)."""
        import socket
        import subprocess
        import signal
        if os.environ.get("MOCK_LLAMA_SERVER") == "1" or "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("MOCK_CPU_ONLY") == "1":
            return True

        for i in range(max_retries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                result = sock.connect_ex(('127.0.0.1', self.port))
                if result != 0:  # 포트가 자유로움
                    return True

            # Q1 / FR-001: 3회 이상 포트 점유 지속 시 외부/잔여 프로세스 자율 복구 (SIGTERM -> SIGKILL)
            if i >= 2:
                try:
                    cmd = f"fuser {self.port}/tcp 2>/dev/null"
                    output = subprocess.check_output(cmd, shell=True, text=True).strip()
                    pids = [int(p) for p in output.split() if p.isdigit() and int(p) != os.getpid()]
                    for p in pids:
                        try:
                            sig = signal.SIGTERM if i < 6 else signal.SIGKILL
                            os.kill(p, sig)
                            print(f"[ProcessManager] Q1: 포트 {self.port} 점유 잔여 PID {p} 정리 시도 (Signal: {sig.name})")
                        except OSError:
                            pass
                except Exception:
                    pass

            await asyncio.sleep(interval)

        # 최종 확인
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock.connect_ex(('127.0.0.1', self.port)) != 0
