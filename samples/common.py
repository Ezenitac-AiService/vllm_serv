"""samples/common.py - vllm_serv 교육용 예제 스크립트 공통 헬퍼 모듈

비전공자 훈련생을 위한 초급 AI 서비스 개발 수업 전용 공통 모듈입니다.
서버 연결 상태(헬스체크)를 사전 점검하고 터미널 콘솔 출력을 직관적으로 가공해 줍니다.
"""

import os
import sys
import json
from pathlib import Path
import httpx


def get_server_host() -> str:
    """vllm_serv 서버 호스트 주소를 반환합니다.
    
    우선순위:
    1. 시스템 환경변수 (SERVER_HOST, OPENAI_BASE_URL, VLLM_API_BASE)
    2. samples/.env 파일
    3. samples/config.json 파일
    4. 기본 안전 주소 (http://127.0.0.1)
    """
    # 1. 시스템 환경변수 확인
    env_host = os.getenv("SERVER_HOST") or os.getenv("OPENAI_BASE_URL") or os.getenv("VLLM_API_BASE")
    if env_host:
        return _format_host_url(env_host)

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

    # 4. 기본 안전 서빙 주소 (하드코딩 배제, 127.0.0.1 기본 폴백)
    return "http://127.0.0.1"


def _format_host_url(host: str) -> str:
    """주소 문자열에 http:// 스킴 적용 및 샘플 스크립트 {SERVER_HOST}:{PORT} 구성을 위한 순수 호스트 주소(http://IP)를 반환합니다."""
    host = host.strip().rstrip("/")
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    
    parts = host.split("://", 1)
    scheme = parts[0]
    rest = parts[1]
    if ":" in rest:
        rest = rest.split(":", 1)[0]
    return f"{scheme}://{rest}"


def check_server_health(host: str = None, port: int = 8081, service_name: str = "vllm_serv 메인 API") -> bool:
    """지정된 포트의 헬스체크(/health, /v1/models)를 수행하여 연결 준비 상태를 확인합니다."""
    if host is None:
        host = get_server_host()
    else:
        host = _format_host_url(host)

    target_base = f"{host}:{port}"

    for endpoint in ["/health", "/v1/models"]:
        url = f"{target_base}{endpoint}"
        try:
            resp = httpx.get(url, timeout=3.0, headers={"Connection": "close"})
            if resp.status_code == 200:
                return True
            if resp.status_code == 503:
                print(f"⚠️ [{service_name}] 서버 백엔드 모델 로딩 중... (잠시 후 다시 시도)")
                return False
        except (httpx.ConnectError, httpx.TimeoutException):
            continue

    print(f"❌ [{service_name}] 서버 포트({port}) 연결 실패 (대상: {target_base})")
    print("👉 서버 구동 상태 확인: ./status_server.sh")
    print("👉 서버 데몬 가동 명령어: ./start_server.sh")
    print("👉 samples/config.json 설정 주소 확인 필요 (예: \"server_host\": \"http://10.0.0.41:8081\")")
    return False


def print_section_header(title: str) -> None:
    """비전공자 훈련생의 시각적 식별성을 높이는 터미널 섹션 헤더를 출력합니다."""
    print("\n" + "=" * 65)
    print(f"📌 {title}")
    print("=" * 65)
