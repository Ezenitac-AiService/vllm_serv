import os
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--real",
        action="store_true",
        default=False,
        help="Run tests in Real GPU Execution Mode (spawning real llama-server subprocesses)"
    )
    parser.addoption(
        "--real-network",
        action="store_true",
        default=False,
        help="Run tests in Real Network & OS Firewall Verification Mode (physical host IP)"
    )

@pytest.fixture
def test_mode(request):
    is_real = request.config.getoption("--real") or os.environ.get("TEST_MODE") == "real"
    return "real" if is_real else "mock"

@pytest.fixture
def is_real_network(request):
    return request.config.getoption("--real-network") or os.environ.get("REAL_NETWORK_TEST") == "1"

@pytest.fixture
def target_host_ip():
    return os.environ.get("HOST_IP", "10.0.0.41")

@pytest.fixture
def base_url(target_host_ip):
    return f"http://{target_host_ip}:8081"


