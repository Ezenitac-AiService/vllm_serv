from fastapi import FastAPI, Response, status
from src.core.llama_manager import llama_manager
from src.core.config_manager import ConfigManager
from src.api.routes.inference_api import router as inference_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="vllm_serv Qwen3.5 & Gemma4 GPU Serving API",
        description="llama.cpp 기반 Qwen 3.5 & Gemma 4 GPU 서빙 API",
        version="1.0.0"
    )

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

    @app.on_event("startup")
    async def startup_event():
        """Auto-load default resident model (qwen3.5-4b) on server startup."""
        import asyncio
        asyncio.create_task(llama_manager.ensure_default_model_resident("qwen3.5-4b"))

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    cm = ConfigManager()
    server_cfg = cm.get_server_config()
    port = server_cfg.get("port", 8081) if server_cfg else 8081
    host = server_cfg.get("host", "0.0.0.0") if server_cfg else "0.0.0.0"
    uvicorn.run("src.api.server:app", host=host, port=port, reload=False)
