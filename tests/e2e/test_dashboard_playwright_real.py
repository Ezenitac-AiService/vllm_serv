"""
E2E Real LAN IP Test for http://10.0.0.41:8081/dashboard/.
Validates HTTP 200 OK response, HTML DOM content rendering, and API health status per Constitution v1.4.0.
"""

import os
import httpx
import pytest

REAL_LAN_IP = "10.0.0.41"
SERVER_PORT = 8081
DASHBOARD_URL = f"http://{REAL_LAN_IP}:{SERVER_PORT}/dashboard/"
HEALTH_URL = f"http://{REAL_LAN_IP}:{SERVER_PORT}/health"


def test_real_lan_ip_dashboard_http_e2e():
    """Verifies that the dashboard HTML and health endpoints are accessible via real LAN IP (10.0.0.41:8081)."""
    with httpx.Client(timeout=10.0) as client:
        # 1. Healthcheck Endpoint Verification
        res_health = client.get(HEALTH_URL)
        assert res_health.status_code == 200, f"Healthcheck expected HTTP 200 OK, got {res_health.status_code}"
        health_json = res_health.json()
        assert health_json.get("status") == "alive", "Healthcheck status should be 'alive'"

        # 2. Real LAN IP Dashboard UI Access Verification
        res_dash = client.get(DASHBOARD_URL)
        assert res_dash.status_code == 200, f"Dashboard UI expected HTTP 200 OK, got {res_dash.status_code}"
        html_content = res_dash.text
        assert "<title>" in html_content or "<html" in html_content.lower(), "Dashboard HTML body should contain valid DOM structure"
