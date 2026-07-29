import os
import asyncio
import httpx
from fastapi import FastAPI, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from src.api.routes.inference_api import router as inference_router
from src.api.routes.dashboard_api import router as dashboard_router
from src.core.llama_manager import llama_manager

LLAMA_SERVER_PORT = 8081
LLAMA_SERVER_URL = f"http://127.0.0.1:{LLAMA_SERVER_PORT}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # FR-004 & T016: Initialize singleton httpx.AsyncClient with connection limits
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    app.state.http_client = httpx.AsyncClient(
        base_url=LLAMA_SERVER_URL,
        limits=limits,
        timeout=None
    )

    # FR-006: 평상시 기본 서비스 모델(qwen3.5-4b)을 GPU VRAM 상주 서빙으로 자동 로드
    cfg = llama_manager.config_manager.get_config()
    current_model = cfg.get("current_model") or "qwen3.5-4b"
    asyncio.create_task(llama_manager.ensure_default_model_resident(current_model))

    yield

    # FR-004: Explicit aclose() teardown on shutdown to prevent socket leaks
    await app.state.http_client.aclose()
    await llama_manager.unload_model()

app = FastAPI(title="vLLM Config Dashboard", lifespan=lifespan)

app.include_router(inference_router)
app.include_router(dashboard_router)

# Mount static dashboard files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/dashboard", StaticFiles(directory=STATIC_DIR, html=True), name="dashboard")

@app.get("/health/liveness")
async def liveness():
    """K8s/LiteLLM Liveness probe (FR-013). Returns 200 OK if server process is running."""
    return {"status": "alive", "pid": llama_manager.process_manager.state.pid}

@app.get("/health/readiness")
async def readiness(response: Response):
    """K8s/LiteLLM Readiness probe (FR-013). Returns 200 OK if 100% VRAM offloaded and state is READY."""
    if llama_manager.is_ready():
        return {
            "status": "ready",
            "vram_offloaded_100pct": True,
            "model_id": llama_manager.process_manager.state.model_id
        }
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "not_ready",
        "vram_offloaded_100pct": False,
        "current_state": llama_manager.state
    }

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard/")
