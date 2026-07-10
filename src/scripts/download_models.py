"""
모델 다운로더 스크립트.
.env 파일에서 HF_TOKEN을 자동으로 로드하여 Hugging Face 모델을 다운로드합니다.
"""
import os
import sys

# Add the project root to the python path so we can import src.core.config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from huggingface_hub import snapshot_download
from src.core.config import SUPPORTED_MODELS, MODELS_DIR, get_hf_token


def download_models():
    """HF_TOKEN을 .env에서 로드하고, 지원 모델을 순차적으로 다운로드합니다."""
    token = get_hf_token()
    print(f"Downloading models to {MODELS_DIR}...")

    for model_id, config in SUPPORTED_MODELS.items():
        model_dir = os.path.join(MODELS_DIR, model_id)
        print(f"Checking {model_id} ({config.repo_id})...")

        # Skip if already downloaded
        if os.path.exists(model_dir):
            gguf_files = [f for f in os.listdir(model_dir) if f.endswith(".gguf")]
            if gguf_files:
                print(f"  Already exists: {os.path.join(model_dir, gguf_files[0])}")
                continue

        print(f"  Downloading from {config.repo_id}...")
        try:
            download_dir = snapshot_download(
                repo_id=config.repo_id,
                allow_patterns=["*.gguf"],
                local_dir=model_dir,
                token=token,
            )
            print(f"  Successfully downloaded {model_id} to {download_dir}")
        except Exception as e:
            print(f"  Error downloading {model_id}: {e}")


if __name__ == "__main__":
    download_models()
