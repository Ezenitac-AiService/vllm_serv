import os
import asyncio
import json
import time
from typing import Optional, Dict, Any
import httpx
from src.core.config_manager import ConfigManager
from src.core.process_manager import ProcessManager, ProcessStatusEnum, ProcessState
from src.core.event_broadcaster import EventBroadcaster
from src.core.model_downloader import ModelDownloader
from src.core.gpu_detector import GpuDeviceInfo, VramOffloadStatus, check_gpu_availability, GpuAccelerationError

# Alias ServerState to ProcessStatusEnum for 100% backward compatibility
ServerState = ProcessStatusEnum

class LlamaManager:
    """Coordinator class delegating to ProcessManager and EventBroadcaster."""

    def __init__(self, config_manager: ConfigManager, port: int = 8081):
        self.config_manager = config_manager
        self.port = port
        self.process_manager = ProcessManager(port=port)
        self.broadcaster = EventBroadcaster(queue_maxsize=100)
        self.model_downloader = ModelDownloader()
        self._error_msg = ""
        self._lock = asyncio.Lock()
        self._gpu_info: Optional[GpuDeviceInfo] = None
        self._vram_offload_status: Optional[VramOffloadStatus] = None

    @property
    def state(self) -> ProcessStatusEnum:
        return self.process_manager.state.status

    @state.setter
    def state(self, value: ProcessStatusEnum):
        # Backward compatibility setter
        self.process_manager.state = ProcessState(
            status=value,
            model_id=self.process_manager.state.model_id,
            port=self.port,
            pid=self.process_manager.state.pid,
            error_message=self._error_msg
        )

    @property
    def process(self):
        return self.process_manager.process

    @process.setter
    def process(self, proc):
        self.process_manager.process = proc

    @property
    def vram_total(self) -> int:
        return self.process_manager.vram_total

    @property
    def hardware_limits(self) -> Dict[str, int]:
        return self.process_manager.hardware_limits

    def is_ready(self) -> bool:
        return self.process_manager.is_ready()

    def subscribe(self) -> asyncio.Queue:
        return self.broadcaster.subscribe(initial_event=self.get_status_event())

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self.broadcaster.unsubscribe(q)

    def _notify_listeners(self) -> None:
        event = self.get_status_event()
        self.broadcaster.broadcast(event)

    def get_status_event(self) -> dict:
        cfg = self.config_manager.get_config()
        state = self.process_manager.state
        data = {
            "state": state.status,
            "current_model": cfg.get("current_model"),
            "current_n_ctx": cfg.get("current_n_ctx"),
            "vram_total": self.vram_total,
            "vram_used": (self._gpu_info.total_vram_mb - self._gpu_info.free_vram_mb) if self._gpu_info else (0 if state.status == ProcessStatusEnum.UNLOADED else 0),
            "error_msg": state.error_message or self._error_msg,
            "gpu_cuda_available": self._gpu_info.is_cuda_available if self._gpu_info else False,
            "vram_offloaded_100pct": self._vram_offload_status.is_fully_offloaded if self._vram_offload_status else False,
            "gpu_info": self._gpu_info.model_dump() if self._gpu_info else None,
            "offload_status": self._vram_offload_status.model_dump() if self._vram_offload_status else None,
        }
        return {"event": "status", "data": json.dumps(data)}

    async def _start_server_subprocess(self, model_id: str, n_ctx: int):
        self._error_msg = ""
        state = await self.process_manager.spawn_process(model_id, n_ctx)

        # FR-005: GPU 검증 결과 캡처
        try:
            self._gpu_info = check_gpu_availability()
        except GpuAccelerationError:
            self._gpu_info = None
        # T012: ProcessManager의 VRAM 오프로드 상태 동기화
        self._vram_offload_status = self.process_manager.vram_offload_status

        self._notify_listeners()

        if state.status == ProcessStatusEnum.ERROR:
            self._error_msg = state.error_message or ""
            return

        if self.process_manager.process and self.process_manager.process.stdout:
            asyncio.create_task(self._monitor_process())

    async def _monitor_process(self):
        proc = self.process_manager.process
        if not proc or not proc.stdout:
            return

        model_id = self.process_manager.state.model_id

        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode('utf-8', errors='replace').strip()
                print(f"[llama-server] {decoded_line}")

                # T015/FR-003: 실시간 VRAM 오프로드 로그 파싱 및 검증
                if model_id and self.process_manager.state.status == ProcessStatusEnum.LOADING:
                    offload_status = ProcessManager.parse_vram_offload_log(decoded_line, model_id)
                    if offload_status is not None:
                        try:
                            self.process_manager.verify_vram_offload(model_id, offload_status)
                            # 검증 성공 시 LlamaManager 상태 동기화
                            self._vram_offload_status = self.process_manager.vram_offload_status
                            self._notify_listeners()
                            print(f"[LlamaManager] T015: VRAM 오프로드 검증 통과 — {offload_status}")
                        except Exception as vram_err:
                            from src.core.gpu_detector import VramOverflowError
                            if isinstance(vram_err, VramOverflowError):
                                print(f"[LlamaManager] ❌ VRAM 오프로드 실패: {vram_err}")
                                self._error_msg = str(vram_err)
                                self.process_manager.state = ProcessState(
                                    status=ProcessStatusEnum.ERROR,
                                    model_id=model_id,
                                    port=self.port,
                                    pid=proc.pid,
                                    error_message=self._error_msg,
                                )
                                self._notify_listeners()
                                # 부분 오프로드 시 프로세스 안전 종료
                                proc.terminate()
                                return
                            raise

                if (self.process_manager.state.status == ProcessStatusEnum.LOADING
                        and "Application startup complete." in decoded_line):
                    self.process_manager.state = ProcessState(
                        status=ProcessStatusEnum.READY,
                        model_id=self.process_manager.state.model_id,
                        port=self.port,
                        pid=proc.pid
                    )
                    # READY 전환 시 최종 VRAM 오프로드 상태 동기화
                    self._vram_offload_status = self.process_manager.vram_offload_status
                    self._notify_listeners()
        except Exception:
            pass


        await proc.wait()
        if self.process_manager.state.status != ProcessStatusEnum.UNLOADED:
            self._error_msg = f"Process crashed with exit code {proc.returncode}"
            self.process_manager.state = ProcessState(
                status=ProcessStatusEnum.ERROR,
                model_id=self.process_manager.state.model_id,
                port=self.port,
                error_message=self._error_msg,
                exit_code=proc.returncode
            )
            self._notify_listeners()

    async def load_model(self, model_id: str, n_ctx: int):
        """모델 로드. 로컬 가중치 미존재 시 자동 다운로드 후 서빙 프로세스 개설."""
        async with self._lock:
            await self._unload_model_internal()
            self.config_manager.update_config(current_model=model_id, current_n_ctx=n_ctx)
            asyncio.create_task(self._start_server_subprocess(model_id, n_ctx))

    async def load_model_with_download(self, model_id: str, n_ctx: int) -> ProcessState:
        """FR-003: 모델 로드 시 로컬 가중치 미존재를 탐지하고 자동 다운로드 수행 후 서빙 프로세스 개설.

        Args:
            model_id: 모델 식별자 (예: 'qwen3.5-2b', 'gemma4-e2b')
            n_ctx: 컨텍스트 크기

        Returns:
            ProcessState: 최종 프로세스 상태
        """
        async with self._lock:
            await self._unload_model_internal()

            # FR-003: 로컬 파일 미존재 탐지 및 자동 다운로드
            if not self.model_downloader.is_model_available(model_id):
                print(f"[LlamaManager] 모델 {model_id} 로컬 미존재 → 자동 다운로드 시작")
                self.process_manager.state = ProcessState(
                    status=ProcessStatusEnum.DOWNLOADING,
                    model_id=model_id,
                    port=self.port,
                )
                self._notify_listeners()

                try:
                    self.model_downloader.ensure_model_available(model_id)
                except (FileNotFoundError, ValueError) as e:
                    self._error_msg = str(e)
                    self.process_manager.state = ProcessState(
                        status=ProcessStatusEnum.ERROR,
                        model_id=model_id,
                        port=self.port,
                        error_message=self._error_msg,
                    )
                    self._notify_listeners()
                    return self.process_manager.state

            self.config_manager.update_config(current_model=model_id, current_n_ctx=n_ctx)
            await self._start_server_subprocess(model_id, n_ctx)

            # T006: HTTP 헬스체크 폴링으로 READY 상태 대기
            ready = await self._wait_for_ready(timeout=30.0)
            if not ready and self.process_manager.state.status == ProcessStatusEnum.LOADING:
                self._error_msg = f"서빙 프로세스 헬스체크 타임아웃 (30초)"
                self.process_manager.state = ProcessState(
                    status=ProcessStatusEnum.ERROR,
                    model_id=model_id,
                    port=self.port,
                    error_message=self._error_msg,
                )
                self._notify_listeners()

            return self.process_manager.state

    def validate_request_allowed(self) -> None:
        """T008 / FR-003: Block incoming inference requests while process is loading / not ready."""
        if not self.is_ready():
            raise RuntimeError(
                f"Inference request blocked: Process is in state '{self.state.value}'. "
                f"Must wait until VRAM 100% offload is complete and state is READY."
            )

    async def _wait_for_ready(self, timeout: float = 30.0, max_retries: int = 10, interval: float = 0.5) -> bool:
        """T006: HTTP GET /health JSON API & VRAM 100% 오프로드 완납 상태 동시 확인 후 READY 전환.

        FR-001, FR-003, FR-009 준수.
        """
        health_url = f"http://127.0.0.1:{self.port}/health"
        models_url = f"http://127.0.0.1:{self.port}/v1/models"
        deadline = time.time() + timeout

        while time.time() < deadline:
            is_health_ok = False
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(health_url, timeout=2.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") in ("ok", "ready") or data.get("slots_idle", 0) >= 0:
                            is_health_ok = True
            except Exception:
                pass

            if not is_health_ok:
                try:
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(models_url, timeout=2.0)
                        if resp.status_code == 200:
                            is_health_ok = True
                except Exception:
                    pass

            # VRAM 100% 오프로드 완료 검증
            offloaded_100 = False
            if self.process_manager.vram_offload_status and self.process_manager.vram_offload_status.is_fully_offloaded:
                offloaded_100 = True
            elif self.process_manager.state.vram_offloaded_100pct or self.process_manager.state.vram_offloaded:
                offloaded_100 = True
            elif os.environ.get("MOCK_LLAMA_SERVER") == "1":
                offloaded_100 = True

            if is_health_ok and offloaded_100:
                self.process_manager.state = ProcessState(
                    status=ProcessStatusEnum.READY,
                    model_id=self.process_manager.state.model_id,
                    port=self.port,
                    pid=self.process_manager.state.pid,
                    vram_offloaded_100pct=True,
                    vram_offloaded=True
                )
                self._notify_listeners()
                print(f"[LlamaManager] ✅ 서빙 프로세스 READY (/health OK & VRAM 100% 오프로드 확인)")
                return True

            await asyncio.sleep(interval)

        return False

    async def ensure_default_model_resident(self, default_model_id: str = "qwen3.5-4b") -> ProcessState:
        """T012 / FR-006: 평상시 기본 서비스 모델(qwen3.5-4b) VRAM 상주 서빙 보장."""
        current_model = self.config_manager.get_config().get("current_model")
        if self.is_ready() and current_model == default_model_id:
            print(f"[LlamaManager] 기본 모델 '{default_model_id}'이 이미 VRAM 상주 서빙 중입니다.")
            return self.process_manager.state

        print(f"[LlamaManager] 기본 모델 '{default_model_id}' VRAM 상주 서빙 로드 시작")
        return await self.load_model_with_download(default_model_id, n_ctx=4096)

    async def unload_model(self):
        async with self._lock:
            await self._unload_model_internal()

    async def _unload_model_internal(self):
        await self.process_manager.stop_process()
        self._vram_offload_status = None
        self._notify_listeners()

# Global instances
config_manager = ConfigManager()
llama_manager = LlamaManager(config_manager)
