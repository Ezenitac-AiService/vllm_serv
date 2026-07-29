import importlib

def test_no_circular_imports():
    """FR-003: src/api, src/core, src/eval 모듈 수입 시 순환 참조가 발생하지 않음을 검증."""
    core_modules = [
        "src.core.config_manager",
        "src.core.gpu_detector",
        "src.core.model_downloader",
        "src.core.process_manager",
        "src.core.llama_manager",
    ]
    api_modules = [
        "src.api.middleware.subnet_filter",
        "src.api.routes.inference_api",
        "src.api.server",
    ]
    eval_modules = [
        "src.eval.quality_evaluator",
    ]

    for mod in core_modules + api_modules + eval_modules:
        m = importlib.import_module(mod)
        assert m is not None
