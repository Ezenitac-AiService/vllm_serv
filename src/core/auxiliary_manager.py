"""
Auxiliary Model Manager for Embedding and Reranker instances (FR-001, FR-006, FR-007).
Manages multi-instance llama-server subprocesses on dedicated ports (8090 for bge-m3, 8091 for bge-reranker-v2-m3),
including background healthchecking and automatic crash recovery.
"""

import asyncio
import os
import time
from typing import Optional, Dict, Any
import httpx

from src.core.config_manager import ConfigManager
from src.core.process_manager import ProcessManager, ProcessStatusEnum, ProcessState
from src.core.model_downloader import ModelDownloader


class AuxiliaryModelManager:
    """Manages dedicated background llama-server instances for embedding and reranking tasks."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        server_cfg = self.config_manager.get_server_config()

        self.embedding_port = server_cfg.get("embedding_backend_port", 8090)
        self.rerank_port = server_cfg.get("rerank_backend_port", 8091)
        self.embedding_enabled = server_cfg.get("embedding_enabled", True)
        self.rerank_enabled = server_cfg.get("rerank_enabled", True)

        self.embedding_pm = ProcessManager(port=self.embedding_port, config_manager=self.config_manager)
        self.rerank_pm = ProcessManager(port=self.rerank_port, config_manager=self.config_manager)

        self.model_downloader = ModelDownloader(config_manager=self.config_manager)
        self._recovery_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def ensure_embedding_resident(self, model_id: str = "bge-m3", n_ctx: int = 8192) -> ProcessState:
        """FR-006: Ensure BGE-M3 embedding instance is loaded and ready on port 8090."""
        if not self.embedding_enabled:
            return self.embedding_pm.state

        if self.embedding_pm.is_ready():
            return self.embedding_pm.state

        # Download if missing
        if not self.model_downloader.is_model_available(model_id):
            print(f"[AuxiliaryManager] Downloading embedding model {model_id}...")
            self.model_downloader.download_model(model_id)

        print(f"[AuxiliaryManager] Spawning embedding instance ({model_id}) on port {self.embedding_port}...")
        state = await self.embedding_pm.spawn_process(model_id=model_id, n_ctx=n_ctx)

        if os.environ.get("MOCK_LLAMA_SERVER"):
            self.embedding_pm.state = ProcessState(
                status=ProcessStatusEnum.READY,
                model_id=model_id,
                port=self.embedding_port,
                vram_offloaded=True,
                vram_offloaded_100pct=True
            )
            return self.embedding_pm.state

        # Poll health until ready
        await self._poll_health(self.embedding_port, self.embedding_pm)
        return self.embedding_pm.state

    async def ensure_rerank_resident(self, model_id: str = "bge-reranker-v2-m3", n_ctx: int = 8192) -> ProcessState:
        """FR-006: Ensure BGE-Reranker-v2-M3 instance is loaded and ready on port 8091."""
        if not self.rerank_enabled:
            return self.rerank_pm.state

        if self.rerank_pm.is_ready():
            return self.rerank_pm.state

        # Download if missing
        if not self.model_downloader.is_model_available(model_id):
            print(f"[AuxiliaryManager] Downloading reranker model {model_id}...")
            self.model_downloader.download_model(model_id)

        print(f"[AuxiliaryManager] Spawning reranker instance ({model_id}) on port {self.rerank_port}...")
        state = await self.rerank_pm.spawn_process(model_id=model_id, n_ctx=n_ctx)

        if os.environ.get("MOCK_LLAMA_SERVER"):
            self.rerank_pm.state = ProcessState(
                status=ProcessStatusEnum.READY,
                model_id=model_id,
                port=self.rerank_port,
                vram_offloaded=True,
                vram_offloaded_100pct=True
            )
            return self.rerank_pm.state

        # Poll health until ready
        await self._poll_health(self.rerank_port, self.rerank_pm)
        return self.rerank_pm.state

    async def _poll_health(self, port: int, pm: ProcessManager, timeout_s: int = 30) -> bool:
        """Poll backend health endpoint until process is ready or times out."""
        start_t = time.perf_counter()
        health_url = f"http://127.0.0.1:{port}/health"

        async with httpx.AsyncClient() as client:
            while time.perf_counter() - start_t < timeout_s:
                if pm.process and pm.process.returncode is not None:
                    pm.state = ProcessState(
                        status=ProcessStatusEnum.ERROR,
                        model_id=pm.state.model_id,
                        port=port,
                        error_message=f"Process exited unexpectedly with code {pm.process.returncode}"
                    )
                    return False

                try:
                    resp = await client.get(health_url, timeout=2.0)
                    if resp.status_code == 200:
                        pm.state = ProcessState(
                            status=ProcessStatusEnum.READY,
                            model_id=pm.state.model_id,
                            port=port,
                            pid=pm.process.pid if pm.process else None,
                            vram_offloaded=True,
                            vram_offloaded_100pct=True
                        )
                        return True
                except Exception:
                    pass

                try:
                    resp = await client.get(f"http://127.0.0.1:{port}/v1/models", timeout=2.0)
                    if resp.status_code == 200:
                        pm.state = ProcessState(
                            status=ProcessStatusEnum.READY,
                            model_id=pm.state.model_id,
                            port=port,
                            pid=pm.process.pid if pm.process else None,
                            vram_offloaded=True,
                            vram_offloaded_100pct=True
                        )
                        return True
                except Exception:
                    pass
                await asyncio.sleep(0.5)

        pm.state = ProcessState(
            status=ProcessStatusEnum.ERROR,
            model_id=pm.state.model_id,
            port=port,
            error_message=f"Healthcheck timeout ({timeout_s}s) for port {port}"
        )
        return False

    async def start_auto_startup_and_recovery(self):
        """FR-006 & FR-007: Auto-start embedding and reranker instances and maintain background crash recovery loop."""
        self._is_running = True
        try:
            if self.embedding_enabled:
                asyncio.create_task(self.ensure_embedding_resident("bge-m3"))
            if self.rerank_enabled:
                asyncio.create_task(self.ensure_rerank_resident("bge-reranker-v2-m3"))
        except Exception as e:
            print(f"[AuxiliaryManager] Startup warning: {e}")

        # Start background recovery loop
        self._recovery_task = asyncio.create_task(self._crash_recovery_loop())

    async def _crash_recovery_loop(self):
        """FR-007: Background crash recovery loop auto-restarting failed instances."""
        while self._is_running:
            await asyncio.sleep(5.0)

            # Check Embedding instance
            if self.embedding_enabled and not os.environ.get("MOCK_LLAMA_SERVER"):
                if self.embedding_pm.state.status in (ProcessStatusEnum.READY, ProcessStatusEnum.LOADING):
                    if self.embedding_pm.process and self.embedding_pm.process.returncode is not None:
                        print(f"[AuxiliaryManager] FR-007: Embedding process crash detected! Auto-restarting...")
                        self.embedding_pm.state = ProcessState(status=ProcessStatusEnum.UNLOADED, port=self.embedding_port)
                        await self.ensure_embedding_resident("bge-m3")

            # Check Rerank instance
            if self.rerank_enabled and not os.environ.get("MOCK_LLAMA_SERVER"):
                if self.rerank_pm.state.status in (ProcessStatusEnum.READY, ProcessStatusEnum.LOADING):
                    if self.rerank_pm.process and self.rerank_pm.process.returncode is not None:
                        print(f"[AuxiliaryManager] FR-007: Reranker process crash detected! Auto-restarting...")
                        self.rerank_pm.state = ProcessState(status=ProcessStatusEnum.UNLOADED, port=self.rerank_port)
                        await self.ensure_rerank_resident("bge-reranker-v2-m3")

    async def shutdown(self):
        """Gracefully stop embedding and reranker instances on server shutdown."""
        self._is_running = False
        if self._recovery_task and not self._recovery_task.done():
            self._recovery_task.cancel()

        await self.embedding_pm.stop_process()
        await self.rerank_pm.stop_process()


# Singleton instance
auxiliary_manager = AuxiliaryModelManager()
