import os
from fastapi import APIRouter, Request, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import asyncio

from src.core.llama_manager import llama_manager

# T017 API Token Verification
async def verify_token(request: Request):
    expected_token = os.environ.get("DASHBOARD_TOKEN")
    if not expected_token:
        return True # if not set, ignore auth
        
    token = request.headers.get("Authorization")
    if not token:
        token = request.query_params.get("token")
        
    if token != expected_token and token != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True

router = APIRouter(prefix="/dashboard/api", dependencies=[Depends(verify_token)])

class PresetApply(BaseModel):
    model_id: str
    n_ctx: int

@router.get("/status")
async def get_status(request: Request):
    import json
    return json.loads(llama_manager.get_status_event()["data"])

@router.get("/capabilities")
async def get_capabilities(request: Request):
    # T008 expose limits
    return {
        "vram_total": llama_manager.vram_total,
        "limits": llama_manager.hardware_limits
    }

@router.post("/apply")
async def apply_preset(preset: PresetApply):
    # T006 apply preset
    await llama_manager.load_model(preset.model_id, preset.n_ctx)
    return {"status": "success", "message": "Loading model..."}

@router.post("/unload")
async def unload_model():
    # T014 Unload API
    await llama_manager.unload_model()
    return {"status": "success"}

@router.get("/stream")
async def sse_stream(request: Request):
    # T011 SSE endpoint
    async def event_generator():
        q = llama_manager.subscribe()
        try:
            while True:
                # If client closes connection
                if await request.is_disconnected():
                    break
                event = await q.get()
                yield event
        finally:
            llama_manager.unsubscribe(q)
            
    return EventSourceResponse(event_generator())
