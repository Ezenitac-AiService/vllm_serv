import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from src.core.llama_manager import llama_manager
from src.core.config_manager import ConfigManager
from src.api.routes.inference_api import router as inference_router
from src.api.middleware.subnet_filter import SubnetFilterMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager replacing deprecated on_event."""
    cm = ConfigManager()
    server_cfg = cm.get_server_config()
    default_model = server_cfg.get("default_model", "qwen3.5-4b")
    
    # Auto-load default resident model on startup
    asyncio.create_task(llama_manager.ensure_default_model_resident(default_model))
    yield
    # Cleanup on shutdown
    await llama_manager.unload_model()

def create_app() -> FastAPI:
    app = FastAPI(
        title="vllm_serv Qwen3.5 & Gemma4 GPU Serving API",
        description="llama.cpp 기반 Qwen 3.5 & Gemma 4 GPU 서빙 API",
        version="1.0.0",
        lifespan=lifespan
    )

    # FR-008: 사설 내부망 CIDR 접근제어 미들웨어 장착
    cm = ConfigManager()
    server_cfg = cm.get_server_config()
    allowed_subnets = server_cfg.get("allowed_subnets", ["127.0.0.1", "192.168.0.0/24"])
    app.add_middleware(SubnetFilterMiddleware, allowed_subnets=allowed_subnets)

    app.include_router(inference_router)

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

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    cm = ConfigManager()
    server_cfg = cm.get_server_config()
    port = server_cfg.get("port", 8081) if server_cfg else 8081
    host = server_cfg.get("host", "127.0.0.1") if server_cfg else "127.0.0.1"
    uvicorn.run("src.api.server:app", host=host, port=port, reload=False)
