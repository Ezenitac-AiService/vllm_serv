from fastapi import FastAPI
from src.api.routes import router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Gemma4 QAT Service API",
        description="llama.cpp 기반 Gemma4 모델 서빙 API",
        version="1.0.0"
    )
    
    app.include_router(router)
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 기본 모델 로드 여부를 체크하는 옵션이 있으면 좋음
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
