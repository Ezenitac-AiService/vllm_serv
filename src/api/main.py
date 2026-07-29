import os
import asyncio
import httpx
from fastapi import FastAPI
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

    # FR-008: Load the last configuration on startup
    cfg = llama_manager.config_manager.get_config()
    current_model = cfg.get("current_model")
    current_n_ctx = cfg.get("current_n_ctx", 4096)

    if current_model:
        asyncio.create_task(llama_manager.load_model(current_model, current_n_ctx))

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

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard/")
