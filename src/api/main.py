import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from src.api.routes.inference_api import router as inference_router
from src.api.routes.dashboard_api import router as dashboard_router
from src.core.llama_manager import llama_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # FR-008: Load the last configuration on startup
    cfg = llama_manager.config_manager.get_config()
    current_model = cfg.get("current_model")
    current_n_ctx = cfg.get("current_n_ctx", 4096)
    
    if current_model:
        # Load in background so we don't block server startup
        import asyncio
        asyncio.create_task(llama_manager.load_model(current_model, current_n_ctx))
        
    yield
    
    # Shutdown
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
