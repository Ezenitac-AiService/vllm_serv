#!/usr/bin/env bash
# ==============================================================================
# vllm_serv: 서빙 및 GPU VRAM 상태 확인 스크립트 (status_server.sh)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    BASE_DIR="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../pyproject.toml" ]; then
    BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    BASE_DIR="$(pwd)"
fi
cd "$BASE_DIR"

PID_FILE="$BASE_DIR/vllm_serv.pid"

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

echo -e "${COLOR_CYAN}====================================================${COLOR_NC}"
echo -e "${COLOR_CYAN} ⚡ vllm_serv 서버 및 GPU 상태 리포트${COLOR_NC}"
echo -e "${COLOR_CYAN}====================================================${COLOR_NC}"

PID=""
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
fi

if [ -z "$PID" ] || ! ps -p "$PID" > /dev/null 2>&1; then
    PID=$(pgrep -f "src.api.server" | tail -n 1 || echo "")
fi

if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
    echo -e "프로세스 상태: ${COLOR_GREEN}🟢 구동 중 (RUNNING, PID: $PID)${COLOR_NC}"
else
    echo -e "프로세스 상태: ${COLOR_YELLOW}⚪ 중지됨 (UNLOADED)${COLOR_NC}"
fi

SERVER_HOST=$(uv run python -c "from src.core.config_manager import ConfigManager; print(ConfigManager().get_server_config().get('host', '127.0.0.1'))" 2>/dev/null || echo "127.0.0.1")
SERVER_PORT=$(uv run python -c "from src.core.config_manager import ConfigManager; print(ConfigManager().get_server_config().get('port', 8081))" 2>/dev/null || echo "8081")

echo -e "\n[REST API 헬스체크 (http://$SERVER_HOST:$SERVER_PORT/health)]"
if command -v curl &> /dev/null; then
    curl -s "http://$SERVER_HOST:$SERVER_PORT/health" | python3 -m json.tool 2>/dev/null || echo -e "${COLOR_YELLOW}응답 없음 (서버 미구현 또는 비활성)${COLOR_NC}"
fi

if command -v nvidia-smi &> /dev/null; then
    echo -e "\n[NVIDIA GPU VRAM 실시간 현황]"
    nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader
fi
