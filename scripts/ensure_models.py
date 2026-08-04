#!/usr/bin/env python3
"""
vllm_serv: 필수 GGUF 모델 가중치 자동 점검 및 다운로드 헬퍼 스크립트 (scripts/ensure_models.py)
092-setup-auto-model-download: FR-001, FR-002, FR-003, FR-004, FR-005

Setup.sh 구동 과정에서 start_server.sh 구동에 필요한 3종 필수 모델
(qwen3.5-4b, bge-m3, bge-reranker-v2-m3)의 로컬 존재 여부를 점검하고,
미존재 시 ModelDownloader를 호출하여 원스톱 자동 프로비저닝을 완료합니다.
"""

import sys
import os
import argparse
from typing import Dict, Any, List

# Add base directory to path if running directly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.model_downloader import ModelDownloader, DownloadStatusEnum


# 필수 자동 가동 3종 모델 목록
REQUIRED_MODELS = [
    "qwen3.5-4b",
    "bge-m3",
    "bge-reranker-v2-m3"
]


def ensure_all_models(
    check_only: bool = False,
    auto_download: bool = True,
    base_dir: str = BASE_DIR
) -> Dict[str, Any]:
    """
    3종 필수 GGUF 모델의 존재 유무를 검사하고, 부재 시 자동 다운로드를 수행합니다.

    Args:
        check_only: True일 경우 검사만 진행하고 다운로드를 하지 않음
        auto_download: True일 경우 미존재 모델 자동 다운로드 실행
        base_dir: 레포지토리 루트 경로

    Returns:
        Dict: 모델 검사 및 다운로드 결과 요약
    """
    downloader = ModelDownloader(base_dir=base_dir)
    results = {
        "target_models": REQUIRED_MODELS,
        "all_models_present": True,
        "details": {},
        "download_summary": {
            "total_models": len(REQUIRED_MODELS),
            "present_count": 0,
            "downloaded_count": 0,
            "failed_count": 0
        }
    }

    print("=" * 60)
    print(" 📦 vllm_serv 필수 GGUF 모델 가중치 자동 점검 및 다운로드 파이프라인")
    print("=" * 60)

    for model_id in REQUIRED_MODELS:
        is_available = downloader.is_model_available(model_id)
        if is_available:
            print(f"  ✓ [{model_id}] 로컬 GGUF 모델 가중치 존재 확인 (Smart Skip)")
            results["details"][model_id] = {
                "status": "EXISTS",
                "is_present": True
            }
            results["download_summary"]["present_count"] += 1
        else:
            results["all_models_present"] = False
            results["details"][model_id] = {
                "status": "MISSING",
                "is_present": False
            }
            print(f"  ⚠️ [{model_id}] GGUF 모델 가중치 부재 감지")

            if not check_only and auto_download:
                print(f"  ⚡ [{model_id}] 자동 다운로드 시작 (HuggingFace Hub / ModelScope)...")
                try:
                    task = downloader.download_model(model_id)
                    if task.status == DownloadStatusEnum.COMPLETED or task.status == DownloadStatusEnum.SKIPPED:
                        print(f"  ✓ [{model_id}] 다운로드 및 검증 완료!")
                        results["details"][model_id]["status"] = "DOWNLOADED"
                        results["details"][model_id]["is_present"] = True
                        results["download_summary"]["downloaded_count"] += 1
                    else:
                        print(f"  ❌ [{model_id}] 다운로드 실패: {task.error_message}")
                        results["details"][model_id]["status"] = "FAILED"
                        results["download_summary"]["failed_count"] += 1
                except Exception as e:
                    print(f"  ❌ [{model_id}] 다운로드 중 예외 발생: {e}")
                    results["details"][model_id]["status"] = "FAILED"
                    results["download_summary"]["failed_count"] += 1
            else:
                results["download_summary"]["failed_count"] += 1

    # 재검증
    all_ready = all(v.get("is_present", False) for v in results["details"].values())
    results["all_models_present"] = all_ready

    print("-" * 60)
    if all_ready:
        print("✓ [PROVISIONING COMPLETE] 모든 필수 3종 모델이 준비되었습니다.")
    else:
        print("⚠️ [PROVISIONING INCOMPLETE] 일부 필수 모델 가중치가 부재하거나 다운로드에 실패했습니다.")
        print("  수동 다운로드 가이드: uv run python scripts/benchmark_quality.py --auto-download --real")

    return results


def main():
    parser = argparse.ArgumentParser(description="vllm_serv 필수 GGUF 모델 점검 및 다운로드 헬퍼")
    parser.add_argument("--check-only", action="store_true", help="다운로드를 진행하지 않고 미존재 여부만 검사")
    parser.add_argument("--no-auto-download", action="store_true", help="자동 다운로드 비활성화")
    args = parser.parse_args()

    res = ensure_all_models(
        check_only=args.check_only,
        auto_download=not args.no_auto_download
    )

    if not res["all_models_present"] and args.check_only:
        sys.exit(1)
    elif not res["all_models_present"]:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
