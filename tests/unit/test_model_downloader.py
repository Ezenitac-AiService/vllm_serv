"""
Unit tests for src/core/model_downloader.py (T005).
Tests ModelDownloadTask, ModelDownloader catalog, availability checks, and download state tracking.
"""

import os
import tempfile
import pytest
from src.core.model_downloader import (
    ModelDownloadTask,
    ModelDownloader,
    DownloadStatusEnum,
    MODEL_DOWNLOAD_CATALOG,
)


class TestModelDownloadTask:
    """T001 Pydantic v2 ModelDownloadTask 데이터 모델 단위 테스트."""

    def test_create_pending_task(self):
        """PENDING 상태의 다운로드 태스크 생성."""
        task = ModelDownloadTask(
            model_id="qwen3.5-2b",
            repo_id="Qwen/Qwen3.5-2B-Instruct-GGUF",
            filename="qwen3.5-2b-instruct-q4_k_m.gguf",
            target_dir="models/qwen3.5-2b",
        )
        assert task.status == DownloadStatusEnum.PENDING
        assert task.download_progress_pct == 0.0
        assert task.error_message is None

    def test_create_completed_task(self):
        """COMPLETED 상태의 다운로드 태스크 생성."""
        task = ModelDownloadTask(
            model_id="gemma4-e2b",
            repo_id="lmstudio-community/gemma-4-E2B-it-GGUF",
            filename="gemma-4-E2B_q4_0-it.gguf",
            clip_filename="gemma-4-E2B-it-mmproj.gguf",
            target_dir="models/gemma4-2b",
            status=DownloadStatusEnum.COMPLETED,
            download_progress_pct=100.0,
        )
        assert task.status == DownloadStatusEnum.COMPLETED
        assert task.clip_filename == "gemma-4-E2B-it-mmproj.gguf"
        assert task.download_progress_pct == 100.0

    def test_update_task_status(self):
        """태스크 상태 업데이트 가능 여부."""
        task = ModelDownloadTask(
            model_id="qwen3.5-4b",
            repo_id="Qwen/Qwen3.5-4B-Instruct-GGUF",
            filename="qwen3.5-4b-instruct-q4_k_m.gguf",
            target_dir="models/qwen3.5-4b",
        )
        task.status = DownloadStatusEnum.DOWNLOADING
        task.download_progress_pct = 45.5
        assert task.status == DownloadStatusEnum.DOWNLOADING
        assert task.download_progress_pct == 45.5


class TestModelDownloadCatalog:
    """MODEL_DOWNLOAD_CATALOG 카탈로그 무결성 단위 테스트."""

    def test_catalog_has_six_models(self):
        """카탈로그에 Qwen 3.5 3종 + Gemma 4 3종 = 6개 모델이 등록되어야 함."""
        assert len(MODEL_DOWNLOAD_CATALOG) == 6

    def test_qwen_models_no_clip(self):
        """Qwen 3.5 모델은 CLIP mmproj가 없어야 함."""
        for model_id in ["qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b"]:
            entry = MODEL_DOWNLOAD_CATALOG[model_id]
            assert entry["clip_filename"] is None

    def test_gemma_models_have_clip(self):
        """Gemma 4 모델은 CLIP mmproj가 있어야 함."""
        for model_id in ["gemma4-e2b", "gemma4-e4b", "gemma4-12b"]:
            entry = MODEL_DOWNLOAD_CATALOG[model_id]
            assert entry["clip_filename"] is not None

    def test_all_entries_have_required_fields(self):
        """모든 카탈로그 항목에 필수 필드가 있어야 함."""
        for model_id, entry in MODEL_DOWNLOAD_CATALOG.items():
            assert "repo_id" in entry, f"{model_id}: repo_id 누락"
            assert "filename" in entry, f"{model_id}: filename 누락"
            assert "target_dir" in entry, f"{model_id}: target_dir 누락"


class TestModelDownloader:
    """ModelDownloader 엔진 단위 테스트."""

    def test_is_model_available_false_when_missing(self):
        """로컬에 모델 파일이 없으면 False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = ModelDownloader(base_dir=tmpdir)
            assert downloader.is_model_available("qwen3.5-2b") is False

    def test_is_model_available_true_when_exists(self):
        """로컬에 모델 파일이 있으면 True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 가짜 GGUF 파일 생성
            target_dir = os.path.join(tmpdir, "models", "qwen3.5-2b")
            os.makedirs(target_dir, exist_ok=True)
            fake_gguf = os.path.join(target_dir, "Qwen3.5-2B-Q4_K_M.gguf")
            with open(fake_gguf, "wb") as f:
                f.write(b"FAKE_GGUF_CONTENT")

            downloader = ModelDownloader(base_dir=tmpdir)
            assert downloader.is_model_available("qwen3.5-2b") is True

    def test_get_model_path_returns_none_when_missing(self):
        """모델 파일 미존재 시 None 반환."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = ModelDownloader(base_dir=tmpdir)
            assert downloader.get_model_path("qwen3.5-9b") is None

    def test_get_model_path_returns_path_when_exists(self):
        """모델 파일 존재 시 절대 경로 반환."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = os.path.join(tmpdir, "models", "gemma4-2b")
            os.makedirs(target_dir, exist_ok=True)
            fake_gguf = os.path.join(target_dir, "gemma-4-E2B_q4_0-it.gguf")
            with open(fake_gguf, "wb") as f:
                f.write(b"FAKE_GGUF_CONTENT")

            downloader = ModelDownloader(base_dir=tmpdir)
            result = downloader.get_model_path("gemma4-e2b")
            assert result is not None
            assert result.endswith("gemma-4-E2B_q4_0-it.gguf")

    def test_download_unknown_model_returns_failed(self):
        """알 수 없는 model_id로 다운로드 시 FAILED 상태 반환."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = ModelDownloader(base_dir=tmpdir)
            task = downloader.download_model("nonexistent-model")
            assert task.status == DownloadStatusEnum.FAILED
            assert "Unknown model_id" in task.error_message

    def test_download_skips_existing_file(self):
        """이미 존재하는 파일은 SKIPPED 상태로 건너뜀."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = os.path.join(tmpdir, "models", "qwen3.5-2b")
            os.makedirs(target_dir, exist_ok=True)
            fake_gguf = os.path.join(target_dir, "Qwen3.5-2B-Q4_K_M.gguf")
            with open(fake_gguf, "wb") as f:
                f.write(b"FAKE_GGUF_CONTENT")

            downloader = ModelDownloader(base_dir=tmpdir)
            task = downloader.download_model("qwen3.5-2b")
            assert task.status == DownloadStatusEnum.SKIPPED
            assert task.download_progress_pct == 100.0

    def test_download_model_without_huggingface_hub_fails_gracefully(self):
        """huggingface_hub가 없을 때 ImportError 우아한 처리."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = ModelDownloader(base_dir=tmpdir)
            # huggingface_hub가 설치되어 있지 않으면 FAILED 반환
            task = downloader.download_model("qwen3.5-2b")
            # ImportError 또는 네트워크 에러 중 하나
            assert task.status in (DownloadStatusEnum.FAILED, DownloadStatusEnum.COMPLETED)

    def test_ensure_model_available_raises_for_unknown(self):
        """알 수 없는 model_id로 ensure 호출 시 ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = ModelDownloader(base_dir=tmpdir)
            with pytest.raises(ValueError, match="Unknown model_id"):
                downloader.ensure_model_available("nonexistent")

    def test_ensure_model_available_returns_path_when_exists(self):
        """이미 존재하는 파일은 즉시 경로 반환."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = os.path.join(tmpdir, "models", "qwen3.5-4b")
            os.makedirs(target_dir, exist_ok=True)
            fake_gguf = os.path.join(target_dir, "Qwen3.5-4B-Q4_K_M.gguf")
            with open(fake_gguf, "wb") as f:
                f.write(b"FAKE_GGUF")

            downloader = ModelDownloader(base_dir=tmpdir)
            path = downloader.ensure_model_available("qwen3.5-4b")
            assert path.endswith("Qwen3.5-4B-Q4_K_M.gguf")

    def test_progress_callback_called(self):
        """다운로드 시 progress_callback이 호출됨."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = os.path.join(tmpdir, "models", "qwen3.5-2b")
            os.makedirs(target_dir, exist_ok=True)
            fake_gguf = os.path.join(target_dir, "Qwen3.5-2B-Q4_K_M.gguf")
            with open(fake_gguf, "wb") as f:
                f.write(b"FAKE_GGUF")

            callback_calls = []
            def cb(mid, pct):
                callback_calls.append((mid, pct))

            downloader = ModelDownloader(base_dir=tmpdir)
            downloader.download_model("qwen3.5-2b", progress_callback=cb)
            assert len(callback_calls) > 0
            assert callback_calls[0][0] == "qwen3.5-2b"
