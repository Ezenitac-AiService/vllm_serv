import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class ModelConfig(BaseModel):
    model_id: str
    repo_id: str
    filename: str
    n_ctx: int = 4096


def get_hf_token() -> str:
    """Retrieve HF_TOKEN from environment (loaded via .env). Raises if missing."""
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise EnvironmentError(
            "HF_TOKEN 환경변수가 설정되지 않았습니다. "
            "프로젝트 루트의 .env 파일에 HF_TOKEN=hf_... 형태로 추가하세요."
        )
    return token


# Define the models we want to support
SUPPORTED_MODELS = {
    "gemma4-2b": ModelConfig(
        model_id="gemma4-2b",
        repo_id="google/gemma-4-E2B-it-qat-q4_0-gguf",
        filename=""  # Will be automatically resolved
    ),
    "gemma4-4b": ModelConfig(
        model_id="gemma4-4b",
        repo_id="google/gemma-4-E4B-it-qat-q4_0-gguf",
        filename=""  # Will be automatically resolved
    ),
    "gemma4-12b": ModelConfig(
        model_id="gemma4-12b",
        repo_id="google/gemma-4-12B-it-qat-q4_0-gguf",
        filename=""  # Will be automatically resolved
    )
}

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
os.makedirs(MODELS_DIR, exist_ok=True)
