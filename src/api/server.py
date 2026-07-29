from fastapi import FastAPI, Response, status
from src.core.llama_manager import llama_manager

def create_app() -> FastAPI:
    app = FastAPI(
        title="Gemma4 QAT Service API",
        description="llama.cpp 기반 Gemma4 모델 서빙 API",
        version="1.0.0"
    )
    
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
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 기본 모델 로드 여부를 체크하는 옵션이 있으면 좋음
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
