import os
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--real",
        action="store_true",
        default=False,
        help="Run tests in Real GPU Execution Mode (spawning real llama-server subprocesses)"
    )

@pytest.fixture
def test_mode(request):
    is_real = request.config.getoption("--real") or os.environ.get("TEST_MODE") == "real"
    return "real" if is_real else "mock"

@pytest.fixture
def base_url():
    return "http://localhost:8000"

