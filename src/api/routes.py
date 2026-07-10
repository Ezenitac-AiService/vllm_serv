from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.core.llama_manager import manager

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "gemma4-12b"
    messages: List[ChatMessage]
    max_tokens: int = 100
    temperature: float = 0.7

class ModelSwitchRequest(BaseModel):
    model_id: str

@router.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    if not manager.active_model_id:
        # Load default model if not loaded
        try:
            manager.load_model(req.model)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    try:
        # Format messages for the internal generate function
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in req.messages]
        
        response = manager.generate(
            messages=formatted_messages,
            max_tokens=req.max_tokens,
            temperature=req.temperature
        )
        
        # Make the response format closely match OpenAI
        return response
    except Exception as e:
        # T011: Basic error handling for out of memory (OOM) or invalid inputs
        error_str = str(e).lower()
        if "out of memory" in error_str or "oom" in error_str:
            raise HTTPException(status_code=503, detail="Server is out of memory. Try reducing context length or switching to a smaller model.")
        raise HTTPException(status_code=400, detail=f"Generation failed: {str(e)}")

@router.post("/api/models/switch")
async def switch_model(req: ModelSwitchRequest):
    try:
        result = manager.load_model(req.model_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch model: {str(e)}")
