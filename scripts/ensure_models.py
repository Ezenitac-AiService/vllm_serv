#!/usr/bin/env python3
"""
vllm_serv: 필수 GGUF 모델 가중치 자동 점검 및 다운로드 헬퍼 스크립트 (scripts/ensure_models.py)
095-setup-benchmark-model-selection: FR-001, FR-008, US4

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


# REQUIRED_MODELS export for backward compatibility
REQUIRED_MODELS = ["qwen3.5-4b", "bge-m3", "bge-reranker-v2-m3"]


def get_dynamic_required_models(server_config: Dict[str, Any] = None, catalog: Dict[str, Any] = None) -> List[str]:
    """FR-007: Dynamically resolve required models from server_config.json and model_catalog.json."""
    if server_config is None or catalog is None:
        try:
            from src.core.config_manager import ConfigManager
            cm = ConfigManager()
            server_config = server_config or cm.get_server_config()
            catalog = catalog or cm.get_model_catalog()
        except Exception:
            server_config = server_config or {}
            catalog = catalog or {}

    req_models = []
    main_model = server_config.get("model", "qwen3.5-4b")
    if main_model and main_model in catalog:
        req_models.append(main_model)

    emb_model = server_config.get("embedding_model", "bge-m3")
    if emb_model and emb_model in catalog:
        req_models.append(emb_model)

    rerank_model = server_config.get("rerank_model", "bge-reranker-v2-m3")
    if rerank_model and rerank_model in catalog:
        req_models.append(rerank_model)

    if not req_models:
        req_models = list(REQUIRED_MODELS)

    return list(dict.fromkeys(req_models))


def ensure_all_models(
    check_only: bool = False,
    auto_download: bool = True,
    base_dir: str = BASE_DIR
) -> Dict[str, Any]:
    """
    FR-007 & FR-012: 필수 GGUF 모델의 존재 유무를 검사하고 부재 시 다운로드, 로컬 존재/다운로드 완료 시 카탈로그 메타데이터 동기화.
    """
    downloader = ModelDownloader(base_dir=base_dir)
    target_models = get_dynamic_required_models()

    results = {
        "target_models": target_models,
        "all_models_present": True,
        "details": {},
        "download_summary": {
            "total_models": len(target_models),
            "present_count": 0,
            "downloaded_count": 0,
            "failed_count": 0
        }
    }

    print("=" * 60)
    print(" 📦 vllm_serv 동적 필수 GGUF 모델 가중치 자동 점검 및 다운로드 파이프라인")
    print("=" * 60)

    for model_id in target_models:
        is_available = downloader.is_model_available(model_id)
        if is_available:
            print(f"  ✓ [{model_id}] 로컬 GGUF 모델 가중치 존재 확인 (Smart Skip & FR-012 Sync)")
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
                max_retries = 3
                success = False
                for attempt in range(1, max_retries + 1):
                    try:
                        task = downloader.download_model(model_id)
                        if task.status in (DownloadStatusEnum.COMPLETED, DownloadStatusEnum.SKIPPED):
                            print(f"  ✓ [{model_id}] 다운로드 및 검증 완료!")
                            results["details"][model_id]["status"] = "DOWNLOADED"
                            results["details"][model_id]["is_present"] = True
                            results["download_summary"]["downloaded_count"] += 1
                            success = True
                            break
                        else:
                            print(f"  ⚠️ [{model_id}] 다운로드 시도 {attempt}/{max_retries} 실패: {task.error_message}")
                    except Exception as e:
                        print(f"  ⚠️ [{model_id}] 시도 {attempt}/{max_retries} 예외 발생: {e}")
                    import time
                    time.sleep(2)
                if not success:
                    print(f"  ❌ [{model_id}] 최종 {max_retries}회 재시도 후 다운로드 실패")
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
