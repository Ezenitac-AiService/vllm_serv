import os
import shutil
import pytest
from unittest.mock import patch, MagicMock

from src.core.process_manager import ProcessManager, LlamaServerBinaryInfo


def test_real_system_native_binary_detection():
    """Real system test verifying ProcessManager detects native binary if present on host."""
    info = ProcessManager.verify_and_build_llama_server()
    assert isinstance(info, LlamaServerBinaryInfo)
    # On this host, /usr/local/lib/ollama/llama-server is present
    if os.path.exists("/usr/local/lib/ollama/llama-server"):
        assert info.build_source != "PYTHON_MODULE_FALLBACK"
        assert os.path.exists(info.binary_path)


def test_binary_path_priority_resolution_ollama_path():
    """Unit test verifying /usr/local/lib/ollama/llama-server is detected when shutil.which returns None."""
    def custom_exists(path):
        if path in ("/usr/local/lib/ollama/llama-server", "/opt/ollama/lib/ollama/llama-server"):
            return True
        return False

    def custom_access(path, mode):
        if path in ("/usr/local/lib/ollama/llama-server", "/opt/ollama/lib/ollama/llama-server"):
            return True
        return False

    with patch("shutil.which", return_value=None), \
         patch("os.path.exists", side_effect=custom_exists), \
         patch("os.access", side_effect=custom_access):
        info = ProcessManager.verify_and_build_llama_server()
        assert info.binary_path == "/usr/local/lib/ollama/llama-server"
        assert info.build_source == "OLLAMA_LIB"


def test_binary_path_priority_shutil_which():
    """Unit test verifying shutil.which finding standalone llama-server takes priority if not ollama."""
    with patch("shutil.which", side_effect=lambda cmd: "/usr/bin/llama-server" if cmd == "llama-server" else None), \
         patch("os.path.exists", return_value=True), \
         patch("os.access", return_value=True):
        info = ProcessManager.verify_and_build_llama_server()
        assert info.binary_path == "/usr/bin/llama-server"
        assert info.build_source == "PATH"
