"""vllm_serv 예제 스크립트 공통 헬퍼 모듈 (samples/common.py)

서버 포트 수신 및 연결 상태를 점검하고, 미구동 시 사용법 안내 문구를 출력합니다.
"""

import os
import sys
import httpx
from src.core.network_detector import NetworkDetector


def get_server_host() -> str:
    """서버 호스트 URL 반환 (환경변수 최우선 -> NetworkDetector 듀얼 포트/다중 서브넷 동적 LAN IP -> 오프라인 127.0.0.1 순)."""
    # 1. 환경변수 최우선 확인
    env_host = os.getenv("SERVER_HOST") or os.getenv("OPENAI_BASE_URL") or os.getenv("VLLM_API_BASE")
    if env_host:
        host = env_host.strip()
        if not host.startswith("http://") and not host.startswith("https://"):
            host = f"http://{host}"
        # 포트/패스가 포함된 전체 URL인 경우 scheme + host_ip만 추출
        if ":" in host.replace("http://", "").replace("https://", ""):
            parts = host.split(":")
            if len(parts) >= 2:
                scheme = parts[0]
                ip_part = parts[1].lstrip("/").split("/")[0]
                return f"{scheme}://{ip_part}"
        return host.rstrip("/")

    # 2. NetworkDetector 기반 듀얼 랜포트/다중 서브넷(192.168.0.x / 10.0.0.x) 동적 IP 감지
    active_ips = NetworkDetector.get_active_lan_ips()
    if active_ips:
        return f"http://{active_ips[0]}"

    # 3. 오프라인 루프백 폴백
    return "http://127.0.0.1"


def check_server_health(host: str = None, port: int = 8081, service_name: str = "vllm_serv") -> bool:
    """지정된 서버 포트 헬스체크 수행 (/health 및 /v1/models 지원) 및 연결 실패 시 안내 메시지 출력."""
    if host is None:
        host = get_server_host()

    for endpoint in ["/health", "/v1/models"]:
        url = f"{host}:{port}{endpoint}"
        try:
            resp = httpx.get(url, timeout=3.0, headers={"Connection": "close"})
            if resp.status_code == 200:
                return True
            # 백엔드 엔진 로딩 시 503 프리플라이트 가드 지원
            if resp.status_code == 503:
                print(f"⚠️ [{service_name}] 서버 포트({port})가 백엔드 엔진을 로딩 중입니다.")
                print("   잠시 후 다시 시도해 주세요.")
                return False
        except (httpx.ConnectError, httpx.TimeoutException):
            continue

    print(f"❌ [{service_name}] 서버 포트({port}) 연결 실패 (대상: {host}:{port})!")
    print(f"👉 서버 구동 확인: ./status_server.sh")
    print(f"👉 백그라운드 서버 데몬 시작: ./start_server.sh")
    return False


def print_section_header(title: str) -> None:
    """섹션 구분을 위한 가시성 높은 헤더 출력."""
    print("\n" + "=" * 60)
    print(f"📌 {title}")
    print("=" * 60)
