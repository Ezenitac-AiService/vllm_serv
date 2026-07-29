#!/usr/bin/env bash
# ==============================================================================
# vllm_serv: 백그라운드 데몬 서버 구동 스크립트 (start_server.sh)
# llama.cpp C++ 바이너리 자동 빌드 및 모델 자동 다운로드 파이프라인 수행
# ==============================================================================

set -eo pipefail

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
LOG_FILE="$BASE_DIR/logs/server.log"

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

CURRENT_RUNNING=$(pgrep -f "src.api.server" || true)
if [ -n "$CURRENT_RUNNING" ]; then
    echo -e "${COLOR_YELLOW}[SERVER] 이미 vllm_serv 서버가 구동 중입니다. (PID: $CURRENT_RUNNING)${COLOR_NC}"
    echo -e "종료하려면 './stop_server.sh' 명령을 실행하세요."
    exit 0
fi

echo -e "${COLOR_CYAN}[SERVER] vllm_serv 인퍼런스 서빙 서버 구동 파이프라인을 시작합니다...${COLOR_NC}"
echo -e "${COLOR_GREEN}[SERVER] 1. llama-server 바이너리 빌드 상태 및 모델 가중치 자동 다운로드 파이프라인 가동${COLOR_NC}"
echo -e "${COLOR_GREEN}[SERVER] 2. 기본 VRAM 상주 서빙 모델(qwen3.5-4b) VRAM 100% 오프로드 검증 수행${COLOR_NC}"
echo -e "${COLOR_GREEN}[SERVER] 3. 로그 파일 경로: $LOG_FILE${COLOR_NC}"

mkdir -p "$BASE_DIR/logs"

nohup uv run python -m src.api.server > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
disown $SERVER_PID 2>/dev/null || true
echo "$SERVER_PID" > "$PID_FILE"

echo -e "${COLOR_GREEN}✓ 서버 데몬 백그라운드 구동 성공! (PID: $SERVER_PID)${COLOR_NC}"

# 서빙 준비 완료 대기 (최대 30초)
echo -n "[SERVER] 서빙 READY 상태 대기 중..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8081/health > /dev/null 2>&1 || curl -s http://127.0.0.1:8081/v1/models > /dev/null 2>&1; then
        echo -e "\n${COLOR_GREEN}✓ 서버 준비 완료! (http://127.0.0.1:8081)${COLOR_NC}"
        echo -e "OpenAI API 엔드포인트: http://127.0.0.1:8081/v1/chat/completions"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo -e "\n${COLOR_YELLOW}⚠️ 서버 초기 로딩 진행 중입니다. 로그를 확인하세요: tail -f logs/server.log${COLOR_NC}"
