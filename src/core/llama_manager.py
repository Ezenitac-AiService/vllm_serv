import asyncio
import json
from typing import Optional, Dict, Any
from src.core.config_manager import ConfigManager
from src.core.process_manager import ProcessManager, ProcessStatusEnum, ProcessState
from src.core.event_broadcaster import EventBroadcaster

# Alias ServerState to ProcessStatusEnum for 100% backward compatibility
ServerState = ProcessStatusEnum

class LlamaManager:
    """Coordinator class delegating to ProcessManager and EventBroadcaster."""

    def __init__(self, config_manager: ConfigManager, port: int = 8081):
        self.config_manager = config_manager
        self.port = port
        self.process_manager = ProcessManager(port=port)
        self.broadcaster = EventBroadcaster(queue_maxsize=100)
        self._error_msg = ""
        self._lock = asyncio.Lock()

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
            "vram_used": 0 if state.status == ProcessStatusEnum.UNLOADED else 8000,
            "error_msg": state.error_message or self._error_msg
        }
        return {"event": "status", "data": json.dumps(data)}

    async def _start_server_subprocess(self, model_id: str, n_ctx: int):
        self._error_msg = ""
        state = await self.process_manager.spawn_process(model_id, n_ctx)
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

        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode('utf-8', errors='replace').strip()
                print(f"[llama-server] {decoded_line}")

                if (self.process_manager.state.status == ProcessStatusEnum.LOADING
                        and "Application startup complete." in decoded_line):
                    self.process_manager.state = ProcessState(
                        status=ProcessStatusEnum.READY,
                        model_id=self.process_manager.state.model_id,
                        port=self.port,
                        pid=proc.pid
                    )
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
        async with self._lock:
            await self._unload_model_internal()
            self.config_manager.update_config(current_model=model_id, current_n_ctx=n_ctx)
            asyncio.create_task(self._start_server_subprocess(model_id, n_ctx))

    async def unload_model(self):
        async with self._lock:
            await self._unload_model_internal()

    async def _unload_model_internal(self):
        await self.process_manager.stop_process()
        self._notify_listeners()

# Global instances
config_manager = ConfigManager()
llama_manager = LlamaManager(config_manager)
