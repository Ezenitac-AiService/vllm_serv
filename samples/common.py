"""vllm_serv 예제 스크립트 공통 헬퍼 모듈 (samples/common.py)

서버 포트 수신 및 연결 상태를 점검하고, 미구동 시 사용법 안내 문구를 출력합니다.
"""

import os
import sys
import json
from pathlib import Path
import httpx


def get_server_host() -> str:
    """서버 호스트 URL 반환 (환경변수 최우선 -> .env -> config.json -> 192.168.0.100 기본값 순)."""
    # 1. 시스템 환경변수 최우선 확인 (SERVER_HOST, OPENAI_BASE_URL, VLLM_API_BASE)
    env_host = os.getenv("SERVER_HOST") or os.getenv("OPENAI_BASE_URL") or os.getenv("VLLM_API_BASE")
    if env_host:
        return _format_host_url(env_host)

    samples_dir_env = os.getenv("SAMPLES_DIR")
    if samples_dir_env:
        samples_dir = Path(samples_dir_env)
    else:
        samples_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    # 2. samples/.env 파일 파싱
    env_file = samples_dir / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SERVER_HOST=") or line.startswith("OPENAI_BASE_URL="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return _format_host_url(val)
        except Exception:
            pass

    # 3. samples/config.json 파일 파싱
    config_file = samples_dir / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                val = data.get("server_host") or data.get("api_url")
                if val:
                    return _format_host_url(val)
        except Exception:
            pass

    # 4. 서비스 플랫폼 IP 대역대 기본값 (192.168.0.x)
    return "http://192.168.0.100"


def _format_host_url(host: str) -> str:
    """호스트 URL에 http:// 프로토콜 스킴 및 포트 정제 적용."""
    host = host.strip()
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    if ":" in host.replace("http://", "").replace("https://", ""):
        parts = host.split(":")
        if len(parts) >= 2:
            scheme = parts[0]
            ip_part = parts[1].lstrip("/").split("/")[0]
            return f"{scheme}://{ip_part}"
    return host.rstrip("/")


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
