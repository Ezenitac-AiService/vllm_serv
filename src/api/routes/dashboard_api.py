import os
import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from src.core.llama_manager import llama_manager

async def verify_token(request: Request) -> bool:
    expected_token = os.environ.get("DASHBOARD_TOKEN")
    if not expected_token:
        return True

    token = request.headers.get("Authorization")
    if not token:
        token = request.query_params.get("token")

    if token != expected_token and token != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True

router = APIRouter(prefix="/dashboard/api", dependencies=[Depends(verify_token)])

class PresetApply(BaseModel):
    model_id: str = Field(..., description="모델 ID")
    n_ctx: int = Field(..., description="컨텍스트 크기")

class StatusResponse(BaseModel):
    state: str
    current_model: Any = None
    current_n_ctx: Any = None
    vram_total: int
    vram_used: int
    error_msg: str = ""

class CapabilitiesResponse(BaseModel):
    vram_total: int
    limits: Dict[str, int]

class GenericResponse(BaseModel):
    status: str
    message: str = ""

@router.get("/status", response_model=StatusResponse)
async def get_status(request: Request):
    return json.loads(llama_manager.get_status_event()["data"])

@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities(request: Request):
    return {
        "vram_total": llama_manager.vram_total,
        "limits": llama_manager.hardware_limits
    }

@router.post("/apply", response_model=GenericResponse)
async def apply_preset(preset: PresetApply):
    await llama_manager.load_model(preset.model_id, preset.n_ctx)
    return {"status": "success", "message": "Loading model..."}

@router.post("/unload", response_model=GenericResponse)
async def unload_model():
    await llama_manager.unload_model()
    return {"status": "success", "message": "Unloading model..."}

@router.get("/stream")
async def sse_stream(request: Request):
    async def event_generator():
        q = llama_manager.subscribe()
        try:
            while True:
                if await request.is_disconnected():
                    break
                event = await q.get()
                yield event
        finally:
            llama_manager.unsubscribe(q)

    return EventSourceResponse(event_generator())
