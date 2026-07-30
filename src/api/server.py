"""
FastAPI Server Entrypoint and Factory Module (FR-001, FR-002, FR-008).
Configures routes, SubnetFilterMiddleware, static assets, and lifespan management.
"""

import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from src.core.llama_manager import llama_manager
from src.core.config_manager import ConfigManager
from src.api.routes.inference_api import router as inference_router
from src.api.routes.dashboard_api import router as dashboard_router
from src.api.routes.admin_api import router as admin_router
from src.api.middleware.subnet_filter import SubnetFilterMiddleware
from src.api.middleware.client_access_logger import ClientAccessLogMiddleware


from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager replacing deprecated on_event."""
    cm = ConfigManager()
    server_cfg = cm.get_server_config()
    default_model = server_cfg.get("default_model", "qwen3.5-4b")
    backend_port = server_cfg.get("backend_port", 8089)

    # Initialize singleton httpx.AsyncClient with connection limits & dynamic base_url
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    app.state.http_client = httpx.AsyncClient(
        base_url=f"http://127.0.0.1:{backend_port}",
        limits=limits,
        timeout=None
    )

    # Auto-load default resident model on startup
    asyncio.create_task(llama_manager.ensure_default_model_resident(default_model))
    yield
    # Cleanup on shutdown
    await app.state.http_client.aclose()
    await llama_manager.unload_model()


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance with subnets middleware and routers."""
    app = FastAPI(
        title="vllm_serv Qwen3.5 & Gemma4 GPU Serving API",
        description="llama.cpp 기반 Qwen 3.5 & Gemma 4 GPU 서빙 API",
        version="1.0.0",
        lifespan=lifespan
    )

    # Allow CORS requests from external LAN web clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # FR-001 / FR-002: 클라이언트 요청 및 감사 로깅 미들웨어 장착
    app.add_middleware(ClientAccessLogMiddleware)

    # FR-008 & FR-032: 사설 내부망 CIDR 접근제어 미들웨어 장착
    cm = ConfigManager()
    allowed_subnets = cm.get_allowed_subnets()
    app.add_middleware(SubnetFilterMiddleware, allowed_subnets=allowed_subnets)

    app.include_router(admin_router)
    app.include_router(inference_router)
    app.include_router(dashboard_router)



    # Mount static dashboard files if static dir exists
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="dashboard")

    @app.get("/health")
    @app.get("/health/liveness")
    async def liveness():
        """K8s/LiteLLM Liveness probe. Returns 200 OK if server process is running."""
        return {"status": "alive", "pid": llama_manager.process_manager.state.pid}

    @app.get("/health/readiness")
    async def readiness(response: Response):
        """K8s/LiteLLM Readiness probe. Returns 200 OK if 100% VRAM offloaded and state is READY."""
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
        """Redirect root path to dashboard."""
        return RedirectResponse(url="/dashboard/")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    cm = ConfigManager()
    server_cfg = cm.get_server_config()
    port = server_cfg.get("port", 8081) if server_cfg else 8081
    host = server_cfg.get("host", "127.0.0.1") if server_cfg else "127.0.0.1"
    uvicorn.run("src.api.server:app", host=host, port=port, reload=False)
