import asyncio
import subprocess
import os
import time
import json
from typing import AsyncGenerator
from enum import Enum
from src.core.config_manager import ConfigManager

class ServerState(str, Enum):
    LOADING = "LOADING"
    READY = "READY"
    UNLOADED = "UNLOADED"
    ERROR = "ERROR"

class LlamaManager:
    def __init__(self, config_manager: ConfigManager, port: int = 8081):
        self.config_manager = config_manager
        self.port = port
        self.state = ServerState.UNLOADED
        self.process: subprocess.Popen | None = None
        self._listeners = []
        self._error_msg = ""
        
        # Load the default limits or fetch them
        self.vram_total = 24000
        self.hardware_limits = {
            "gemma-4-E2B-it-qat-q4_0-gguf": 35000,
            "google/gemma-4-E2B-it-qat-q4_0-gguf": 35000,
            "gemma4-12b": 9500
        }
        self._lock = asyncio.Lock()

    def is_ready(self):
        return self.state == ServerState.READY

    def subscribe(self):
        q = asyncio.Queue()
        self._listeners.append(q)
        q.put_nowait(self.get_status_event())
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._listeners:
            self._listeners.remove(q)

    def _notify_listeners(self):
        event = self.get_status_event()
        for q in self._listeners:
            q.put_nowait(event)

    def get_status_event(self) -> dict:
        cfg = self.config_manager.get_config()
        data = {
            "state": self.state,
            "current_model": cfg.get("current_model"),
            "current_n_ctx": cfg.get("current_n_ctx"),
            "vram_total": self.vram_total,
            "vram_used": 0 if self.state == ServerState.UNLOADED else 8000,
            "error_msg": self._error_msg
        }
        return {"event": "status", "data": json.dumps(data)}

    async def _start_server_subprocess(self, model_id: str, n_ctx: int):
        self.state = ServerState.LOADING
        self._error_msg = ""
        self._notify_listeners()
        
        # Map model_id aliases to actual local file paths
        model_paths = {
            "gemma4-e2b": {
                "model": "models/gemma4-2b/gemma-4-E2B_q4_0-it.gguf",
                "clip": "models/gemma4-2b/gemma-4-E2B-it-mmproj.gguf"
            },
            "gemma4-e4b": {
                "model": "models/gemma4-4b/gemma-4-E4B_q4_0-it.gguf",
                "clip": "models/gemma4-4b/gemma-4-E4B-it-mmproj.gguf"
            },
            "gemma4-12b": {
                "model": "models/gemma4-12b/gemma-4-12b-it-qat-q4_0.gguf",
                "clip": "models/gemma4-12b/mmproj-gemma-4-12b-it-qat-q4_0.gguf"
            }
        }
        
        target_paths = model_paths.get(model_id)
        if not target_paths:
            self.state = ServerState.ERROR
            self.error_message = f"Unknown model_id: {model_id}"
            self._notify_listeners()
            return
            
        import os
        base_dir = "/home/dev/vllm_serv"
        model_file = os.path.join(base_dir, target_paths["model"])
        clip_file = os.path.join(base_dir, target_paths["clip"])

        cmd = [
            "python3", "-m", "llama_cpp.server",
            "--model", model_file,
            "--n_ctx", str(n_ctx),
            "--host", "127.0.0.1",
            "--port", str(self.port),
            "--n_gpu_layers", "-1",
            "--clip_model_path", clip_file
        ]
        
        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            # Wait for server to be ready
            while True:
                line = await self.process.stdout.readline()
                if not line:
                    break
                line_str = line.decode('utf-8')
                print(f"[llama-server] {line_str.strip()}")
                if "Uvicorn running on" in line_str or "Application startup complete" in line_str:
                    self.state = ServerState.READY
                    self._notify_listeners()
                    break
            
            asyncio.create_task(self._monitor_process())
            
        except Exception as e:
            self.state = ServerState.ERROR
            self._error_msg = str(e)
            self._notify_listeners()

    async def _monitor_process(self):
        if not self.process: return
        await self.process.wait()
        if self.state != ServerState.UNLOADED:
            self.state = ServerState.ERROR
            self._error_msg = f"Process crashed with exit code {self.process.returncode}"
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
        # Internal call without grabbing the lock
        if self.process:
            try:
                if self.process.returncode is None:
                    self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    if self.process.returncode is None:
                        self.process.kill()
            except ProcessLookupError:
                pass
            self.process = None
        self.state = ServerState.UNLOADED
        self._notify_listeners()

# Global instances
config_manager = ConfigManager()
llama_manager = LlamaManager(config_manager)
