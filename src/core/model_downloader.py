"""
HuggingFace Hub GGUF & mmproj CLIP 자동 다운로더 모듈 (FR-001, FR-002, FR-003).

지원 모델:
  - Qwen 3.5 (2B, 4B, 9B) — q4_k_m GGUF
  - Gemma 4 (E2B, E4B, 12B) — q4_0 GGUF + mmproj CLIP 프로젝터

기능:
  - 로컬 파일 미존재 탐지 및 HuggingFace Hub 자동 다운로드
  - 이어받기(Resume) 및 진행률 콘솔 출력
  - 다운로드 상태 추적 (ModelDownloadTask Pydantic v2 모델)
"""

import os
import shutil
from enum import Enum
from typing import Optional, Dict, List, Callable
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# T001: Pydantic v2 데이터 모델 정의
# ---------------------------------------------------------------------------

class DownloadStatusEnum(str, Enum):
    """다운로드 상태 열거형."""
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"  # 이미 존재


class ModelDownloadTask(BaseModel):
    """단일 모델 다운로드 작업 상태 추적 엔티티."""
    model_config = ConfigDict(frozen=False)

    model_id: str = Field(..., description="모델 식별자 (예: 'qwen3.5-2b')")
    repo_id: str = Field(..., description="HuggingFace Repository ID")
    filename: str = Field(..., description="GGUF 가중치 파일명")
    clip_filename: Optional[str] = Field(default=None, description="CLIP mmproj 파일명 (Gemma 4 전용)")
    target_dir: str = Field(..., description="로컬 저장 디렉토리 (예: 'models/qwen3.5-2b/')")
    status: DownloadStatusEnum = Field(default=DownloadStatusEnum.PENDING, description="다운로드 상태")
    download_progress_pct: float = Field(default=0.0, description="진행률 (0.0 ~ 100.0)")
    error_message: Optional[str] = Field(default=None, description="에러 메시지")


# ---------------------------------------------------------------------------
# HuggingFace Hub 모델 카탈로그
# ---------------------------------------------------------------------------

MODEL_DOWNLOAD_CATALOG: Dict[str, Dict] = {
    "qwen3.5-2b": {
        "repo_id": "Qwen/Qwen3.5-2B-Instruct-GGUF",
        "filename": "qwen3.5-2b-instruct-q4_k_m.gguf",
        "clip_filename": None,
        "target_dir": "models/qwen3.5-2b",
    },
    "qwen3.5-4b": {
        "repo_id": "Qwen/Qwen3.5-4B-Instruct-GGUF",
        "filename": "qwen3.5-4b-instruct-q4_k_m.gguf",
        "clip_filename": None,
        "target_dir": "models/qwen3.5-4b",
    },
    "qwen3.5-9b": {
        "repo_id": "Qwen/Qwen3.5-9B-Instruct-GGUF",
        "filename": "qwen3.5-9b-instruct-q4_k_m.gguf",
        "clip_filename": None,
        "target_dir": "models/qwen3.5-9b",
    },
    "gemma4-e2b": {
        "repo_id": "lmstudio-community/gemma-4-E2B-it-GGUF",
        "filename": "gemma-4-E2B_q4_0-it.gguf",
        "clip_filename": "gemma-4-E2B-it-mmproj.gguf",
        "target_dir": "models/gemma4-2b",
    },
    "gemma4-e4b": {
        "repo_id": "lmstudio-community/gemma-4-E4B-it-GGUF",
        "filename": "gemma-4-E4B_q4_0-it.gguf",
        "clip_filename": "gemma-4-E4B-it-mmproj.gguf",
        "target_dir": "models/gemma4-4b",
    },
    "gemma4-12b": {
        "repo_id": "lmstudio-community/gemma-4-12b-it-GGUF",
        "filename": "gemma-4-12b-it-qat-q4_0.gguf",
        "clip_filename": "mmproj-gemma-4-12b-it-qat-q4_0.gguf",
        "target_dir": "models/gemma4-12b",
    },
}


# ---------------------------------------------------------------------------
# T002: HuggingFace Hub 다운로드 엔진 (FR-001, FR-002)
# ---------------------------------------------------------------------------

class ModelDownloader:
    """HuggingFace Hub 기반 GGUF 및 mmproj CLIP 자동 다운로더.

    FR-001: huggingface_hub API를 통해 GGUF 가중치 및 mmproj CLIP 가중치를 자동 다운로드.
    FR-002: 다운로드 진행 상황(속도, %, 바이트)을 터미널에 시각화.
    FR-003: 모델 로드 요청 시 로컬 가중치 미존재를 탐지하고 자동 다운로드 수행.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """초기화.

        Args:
            base_dir: 프로젝트 루트 디렉토리. None이면 자동 감지.
        """
        if base_dir is None:
            self.base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
        else:
            self.base_dir = base_dir

        self._tasks: Dict[str, ModelDownloadTask] = {}

    @property
    def catalog(self) -> Dict[str, Dict]:
        """다운로드 가능 모델 카탈로그 반환."""
        return MODEL_DOWNLOAD_CATALOG

    def get_task(self, model_id: str) -> Optional[ModelDownloadTask]:
        """특정 모델의 다운로드 상태 조회."""
        return self._tasks.get(model_id)

    def get_all_tasks(self) -> Dict[str, ModelDownloadTask]:
        """전체 다운로드 상태 맵 반환."""
        return dict(self._tasks)

    def is_model_available(self, model_id: str) -> bool:
        """로컬에 해당 모델의 GGUF 가중치 파일이 존재하는지 확인 (FR-003)."""
        catalog_entry = MODEL_DOWNLOAD_CATALOG.get(model_id)
        if not catalog_entry:
            return False
        target_path = os.path.join(
            self.base_dir, catalog_entry["target_dir"], catalog_entry["filename"]
        )
        return os.path.isfile(target_path)

    def get_model_path(self, model_id: str) -> Optional[str]:
        """모델의 로컬 GGUF 파일 절대 경로 반환. 미존재 시 None."""
        catalog_entry = MODEL_DOWNLOAD_CATALOG.get(model_id)
        if not catalog_entry:
            return None
        target_path = os.path.join(
            self.base_dir, catalog_entry["target_dir"], catalog_entry["filename"]
        )
        if os.path.isfile(target_path):
            return target_path
        return None

    def download_model(
        self,
        model_id: str,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        force: bool = False,
    ) -> ModelDownloadTask:
        """단일 모델의 GGUF 가중치(및 CLIP mmproj)를 HuggingFace Hub에서 다운로드.

        Args:
            model_id: 모델 식별자 (예: 'qwen3.5-2b', 'gemma4-e2b')
            progress_callback: 진행률 콜백 함수 (model_id, progress_pct)
            force: True일 경우 이미 존재해도 재다운로드

        Returns:
            ModelDownloadTask: 다운로드 결과 상태
        """
        catalog_entry = MODEL_DOWNLOAD_CATALOG.get(model_id)
        if not catalog_entry:
            task = ModelDownloadTask(
                model_id=model_id,
                repo_id="unknown",
                filename="unknown",
                target_dir="unknown",
                status=DownloadStatusEnum.FAILED,
                error_message=f"Unknown model_id: {model_id}",
            )
            self._tasks[model_id] = task
            return task

        task = ModelDownloadTask(
            model_id=model_id,
            repo_id=catalog_entry["repo_id"],
            filename=catalog_entry["filename"],
            clip_filename=catalog_entry.get("clip_filename"),
            target_dir=catalog_entry["target_dir"],
            status=DownloadStatusEnum.PENDING,
        )
        self._tasks[model_id] = task

        target_dir_abs = os.path.join(self.base_dir, catalog_entry["target_dir"])
        target_file = os.path.join(target_dir_abs, catalog_entry["filename"])

        # FR-003: 로컬 파일 미존재 탐지
        if os.path.isfile(target_file) and not force:
            task.status = DownloadStatusEnum.SKIPPED
            task.download_progress_pct = 100.0
            print(f"[ModelDownloader] {model_id}: 이미 존재함 → {target_file}")
            if progress_callback:
                progress_callback(model_id, 100.0)
            return task

        # 디렉토리 생성
        os.makedirs(target_dir_abs, exist_ok=True)

        task.status = DownloadStatusEnum.DOWNLOADING
        print(f"[ModelDownloader] {model_id}: 다운로드 시작 → {catalog_entry['repo_id']}/{catalog_entry['filename']}")

        try:
            # huggingface_hub 동적 임포트 (런타임 의존성)
            from huggingface_hub import hf_hub_download

            # FR-001: 메인 GGUF 가중치 다운로드
            downloaded_path = hf_hub_download(
                repo_id=catalog_entry["repo_id"],
                filename=catalog_entry["filename"],
                local_dir=target_dir_abs,
                resume_download=True,
            )
            task.download_progress_pct = 80.0
            print(f"[ModelDownloader] {model_id}: GGUF 가중치 다운로드 완료 → {downloaded_path}")
            if progress_callback:
                progress_callback(model_id, 80.0)

            # FR-001: CLIP mmproj 프로젝터 다운로드 (Gemma 4 전용)
            if catalog_entry.get("clip_filename"):
                clip_downloaded = hf_hub_download(
                    repo_id=catalog_entry["repo_id"],
                    filename=catalog_entry["clip_filename"],
                    local_dir=target_dir_abs,
                    resume_download=True,
                )
                print(f"[ModelDownloader] {model_id}: CLIP mmproj 다운로드 완료 → {clip_downloaded}")

            task.status = DownloadStatusEnum.COMPLETED
            task.download_progress_pct = 100.0
            print(f"[ModelDownloader] {model_id}: ✅ 다운로드 완료")
            if progress_callback:
                progress_callback(model_id, 100.0)

        except ImportError:
            task.status = DownloadStatusEnum.FAILED
            task.error_message = (
                "huggingface_hub 패키지가 설치되어 있지 않습니다. "
                "'uv add huggingface_hub' 또는 'pip install huggingface_hub'을 실행하세요."
            )
            print(f"[ModelDownloader] {model_id}: ❌ {task.error_message}")
        except Exception as e:
            task.status = DownloadStatusEnum.FAILED
            task.error_message = str(e)
            print(f"[ModelDownloader] {model_id}: ❌ 다운로드 실패 → {e}")

        return task

    def download_all_models(
        self,
        model_ids: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        skip_existing: bool = True,
    ) -> Dict[str, ModelDownloadTask]:
        """복수 모델 순차 다운로드.

        Args:
            model_ids: 다운로드 대상 모델 ID 목록. None이면 전체 카탈로그.
            progress_callback: 진행률 콜백 함수.
            skip_existing: True면 이미 존재하는 파일 건너뛰기.

        Returns:
            모델별 다운로드 결과 맵.
        """
        targets = model_ids or list(MODEL_DOWNLOAD_CATALOG.keys())
        results: Dict[str, ModelDownloadTask] = {}

        for i, mid in enumerate(targets, 1):
            print(f"\n[ModelDownloader] === [{i}/{len(targets)}] {mid} ===")
            task = self.download_model(
                mid, progress_callback=progress_callback, force=not skip_existing
            )
            results[mid] = task

        return results

    def ensure_model_available(
        self,
        model_id: str,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> str:
        """모델이 로컬에 존재하는지 확인하고, 없으면 자동 다운로드 후 경로 반환 (FR-003).

        Args:
            model_id: 모델 식별자

        Returns:
            GGUF 가중치 파일 절대 경로

        Raises:
            FileNotFoundError: 다운로드 실패 시
            ValueError: 알 수 없는 model_id
        """
        catalog_entry = MODEL_DOWNLOAD_CATALOG.get(model_id)
        if not catalog_entry:
            raise ValueError(f"Unknown model_id: {model_id}")

        target_path = os.path.join(
            self.base_dir, catalog_entry["target_dir"], catalog_entry["filename"]
        )

        # 이미 존재하면 즉시 반환
        if os.path.isfile(target_path):
            return target_path

        # 자동 다운로드 시도
        task = self.download_model(model_id, progress_callback=progress_callback)
        if task.status == DownloadStatusEnum.COMPLETED:
            return target_path
        elif task.status == DownloadStatusEnum.SKIPPED:
            return target_path
        else:
            raise FileNotFoundError(
                f"모델 다운로드 실패 ({model_id}): {task.error_message}"
            )
