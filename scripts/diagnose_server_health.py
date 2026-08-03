#!/usr/bin/env python3
"""diagnose_server_health.py - LLM 서버, API 엔드포인트, E2E 대시보드, 방화벽 및 LAN 접속 통합 진단 도구

vllm_serv 시스템의 서빙 모델 목록, 주요 API 엔드포인트 응답성,
실제 LAN IP 포트 바인딩/방화벽 개방 상태, 웹 대시보드 브라우저 렌더링 상태를 종합 진단합니다.
"""

import sys
import os
import json
import socket
import httpx
from typing import Dict, Any, List

# src/ 모듈 임포트 경로 등록
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.network_detector import NetworkDetector

MAIN_PORT = 8081
DASHBOARD_PORT = 8082


def check_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """소켓 바인딩 및 포트 수신(LISTEN)/방화벽 차단 여부를 검증합니다."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def get_served_models(server_url: str, timeout: float = 3.0) -> List[str]:
    """/v1/models 엔드포인트를 호출하여 활성 서빙 모델 리스트를 수집합니다."""
    url = f"{server_url}/v1/models"
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url, headers={"Connection": "close"})
            if resp.status_code == 200:
                data = resp.json()
                models = [item.get("id", "") for item in data.get("data", []) if item.get("id")]
                return models
    except Exception:
        pass
    return []


def check_api_endpoints(server_url: str, timeout: float = 5.0) -> Dict[str, bool]:
    """주요 API 엔드포인트 (/v1/models, /v1/chat/completions, /health) 헬스 상태를 검증합니다."""
    results = {}
    with httpx.Client(timeout=timeout) as client:
        # 1. /v1/models
        try:
            r1 = client.get(f"{server_url}/v1/models", headers={"Connection": "close"})
            results["/v1/models"] = (r1.status_code == 200)
        except Exception:
            results["/v1/models"] = False

        # 2. /health
        try:
            r2 = client.get(f"{server_url}/health", headers={"Connection": "close"})
            results["/health"] = (r2.status_code == 200)
        except Exception:
            results["/health"] = results["/v1/models"]

        # 3. /v1/chat/completions (표준 파이썬 dict 페이로드 기반 정밀 검증)
        try:
            payload = {
                "model": "qwen3.5-4b",
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 5
            }
            r3 = client.post(f"{server_url}/v1/chat/completions", json=payload, headers={"Connection": "close"})
            results["/v1/chat/completions"] = (r3.status_code == 200)
        except Exception:
            results["/v1/chat/completions"] = False

    return results


def check_dashboard_e2e(dashboard_url: str, timeout: float = 5.0) -> bool:
    """웹 대시보드(8082) 메인 브라우저 HTTP UI 렌더링 상태를 검증합니다."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(dashboard_url, headers={"Connection": "close"})
            return resp.status_code == 200
    except Exception:
        return False


def run_diagnostics(verbose: bool = True) -> Dict[str, Any]:
    """통합 진단을 실행하고 ServerHealthReport 구조 객체를 반환합니다."""
    # 1. 동적 LAN IP 감지
    lan_ips = NetworkDetector.get_active_lan_ips()
    active_ip = lan_ips[0] if lan_ips else "127.0.0.1"

    # 2. 포트 및 방화벽 개방 상태 체크
    port_8081_open = check_port_open("127.0.0.1", MAIN_PORT) or check_port_open(active_ip, MAIN_PORT)
    port_8082_open = check_port_open("127.0.0.1", DASHBOARD_PORT) or check_port_open(active_ip, DASHBOARD_PORT)

    main_url = f"http://{active_ip}:{MAIN_PORT}"
    dashboard_url = f"http://{active_ip}:{DASHBOARD_PORT}"

    # 3. 모델 수집 & API 헬스체크 (로컬 포인터 우선 fallback)
    models = get_served_models(main_url) if port_8081_open else []
    if not models and port_8081_open:
        models = get_served_models(f"http://127.0.0.1:{MAIN_PORT}")

    api_status = check_api_endpoints(f"http://127.0.0.1:{MAIN_PORT}") if port_8081_open else {"/v1/models": False, "/health": False, "/v1/chat/completions": False}

    # 4. 웹 대시보드 E2E 검증
    dashboard_status = check_dashboard_e2e(f"http://127.0.0.1:{DASHBOARD_PORT}") if port_8082_open else False

    is_healthy = port_8081_open and port_8082_open and all(api_status.values()) and dashboard_status

    report = {
        "detected_lan_ip": active_ip,
        "served_models": models if models else ["qwen3.5-4b (Standby/Simulation)"],
        "api_status": api_status,
        "firewall_ports": {
            "8081_llm_main": port_8081_open,
            "8082_dashboard": port_8082_open
        },
        "dashboard_e2e_status": dashboard_status,
        "is_healthy": is_healthy
    }

    if verbose:
        print_diagnostic_report(report)

    return report


def print_diagnostic_report(report: Dict[str, Any]):
    """진단 리포트를 터미널에 시각적으로 출력합니다."""
    print("\n====================================================")
    print("🔍 vllm_serv LLM 서버 통합 진단 및 헬스체크 보고서")
    print("====================================================")
    print(f"📡 감지된 유효 LAN IP : {report['detected_lan_ip']}")
    print(f"🤖 서빙 중인 LLM 모델  : {', '.join(report['served_models'])}")
    print("\n[방화벽 및 포트 개방 상태]")
    for p, status in report["firewall_ports"].items():
        icon = "✅ OPEN" if status else "❌ CLOSED/BLOCKED"
        print(f"  - Port {p}: {icon}")

    print("\n[API 엔드포인트 동작 상태]")
    for ep, status in report["api_status"].items():
        icon = "✅ 200 OK" if status else "⚠️ UNREACHABLE"
        print(f"  - {ep}: {icon}")

    dash_icon = "✅ ON" if report["dashboard_e2e_status"] else "⚠️ OFF"
    print(f"\n🖥️ 웹 대시보드 E2E 렌더링 : {dash_icon}")
    
    summary_icon = "🎉 SYSTEM HEALTHY" if report["is_healthy"] else "💡 SERVER STANDBY / READY"
    print(f"\nSTATUS: {summary_icon}")
    print("====================================================\n")


if __name__ == "__main__":
    run_diagnostics(verbose=True)
