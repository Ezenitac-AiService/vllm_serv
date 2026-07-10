import os
import time
from typing import Optional, Dict, Any
from llama_cpp import Llama
from src.core.config import SUPPORTED_MODELS, MODELS_DIR

class LlamaManager:
    def __init__(self):
        self.active_model_id: Optional[str] = None
        self.llama: Optional[Llama] = None

    def load_model(self, model_id: str) -> Dict[str, Any]:
        """
        Loads the specified model into memory, unloading the previous one if necessary.
        """
        if model_id not in SUPPORTED_MODELS:
            raise ValueError(f"Model ID '{model_id}' is not supported.")
            
        if self.active_model_id == model_id and self.llama is not None:
            return {
                "status": "success",
                "message": f"Model {model_id} is already loaded.",
                "load_time_sec": 0.0
            }

        config = SUPPORTED_MODELS[model_id]
        
        # Find the .gguf file dynamically since we used snapshot_download
        model_dir = os.path.join(MODELS_DIR, model_id)
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found at {model_dir}. Please run download script first.")
            
        gguf_files = [f for f in os.listdir(model_dir) if f.endswith(".gguf") and "mmproj" not in f.lower()]
        if not gguf_files:
            raise FileNotFoundError(f"No .gguf model file found in {model_dir} (mmproj files are excluded)")
            
        model_path = os.path.join(model_dir, gguf_files[0])

        # Unload previous model explicitly
        if self.llama is not None:
            print(f"Unloading active model: {self.active_model_id}")
            del self.llama
            self.llama = None
            self.active_model_id = None

        print(f"Loading model: {model_id} from {model_path}")
        start_time = time.time()
        
        try:
            self.llama = Llama(
                model_path=model_path,
                n_ctx=config.n_ctx,
                n_gpu_layers=-1, # Offload entirely to GPU
                verbose=False
            )
        except Exception as e:
            self.llama = None
            self.active_model_id = None
            raise RuntimeError(f"Failed to load model {model_id}: {e}")
            
        load_time = time.time() - start_time
        self.active_model_id = model_id
        
        return {
            "status": "success",
            "message": f"Model switched to {model_id}",
            "load_time_sec": round(load_time, 2)
        }

    def generate(self, messages: list, max_tokens: int = 100, temperature: float = 0.7):
        """
        Wrapper around Llama's create_chat_completion.
        """
        if self.llama is None:
            raise RuntimeError("No model is currently loaded.")
            
        return self.llama.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

# Global manager instance
manager = LlamaManager()
