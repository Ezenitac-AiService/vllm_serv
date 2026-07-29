#!/usr/bin/env bash
# ==============================================================================
# vllm_serv: 환경 검증, uv 설정, 방화벽 등록 및 서빙 제어 스크립트 생성 원스톱 setup.sh
# ==============================================================================

set -eo pipefail

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

log_info() { echo -e "${COLOR_GREEN}[SETUP INFO]${COLOR_NC} $1"; }
log_warn() { echo -e "${COLOR_YELLOW}[SETUP WARN]${COLOR_NC} $1"; }
log_err()  { echo -e "${COLOR_RED}[SETUP ERROR]${COLOR_NC} $1"; }
log_step() { echo -e "\n${COLOR_CYAN}====================================================${COLOR_NC}\n${COLOR_CYAN}▶ $1${COLOR_NC}\n${COLOR_CYAN}====================================================${COLOR_NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    BASE_DIR="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../pyproject.toml" ]; then
    BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    BASE_DIR="$(pwd)"
fi
cd "$BASE_DIR"

log_step "1. 필수 프로젝트 기본 파일 존재 여부 검증"

REQUIRED_FILES=(
    "pyproject.toml"
    "config/model_catalog.json"
    "config/server_config.json"
    "src/api/server.py"
    "src/core/process_manager.py"
    "src/core/llama_manager.py"
    "scripts/benchmark_quality.py"
)

MISSING_COUNT=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$BASE_DIR/$file" ]; then
        log_info "✓ 필수 파일 존재: $file"
    else
        log_err "✗ 필수 파일 누락: $file"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

if [ "$MISSING_COUNT" -gt 0 ]; then
    log_err "누락된 필수 파일이 $MISSING_COUNT개 있습니다. 레포지토리 상태를 확인하세요."
    exit 1
fi

log_step "2. uv 패키지 매니저 및 파이썬 가상환경 구성"

if ! command -v uv &> /dev/null; then
    log_warn "uv 패키지 매니저가 설치되어 있지 않습니다. 자동 설치를 진행합니다..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

if ! command -v uv &> /dev/null; then
    log_err "uv 설치에 실패했습니다. 수동으로 'curl -LsSf https://astral.sh/uv/install.sh | sh' 명령을 실행하세요."
    exit 1
fi

log_info "uv 버전: $(uv --version)"

log_info "가상환경 패키지 동기화 중 (uv sync)..."
uv sync

log_info "NVIDIA GPU 가속 드라이버 및 nvidia-smi 검증 중..."
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)
    VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -n 1)
    log_info "✓ NVIDIA GPU 감지 완료: $GPU_NAME (총 VRAM: $VRAM_TOTAL)"
else
    log_warn "nvidia-smi 명령어를 찾을 수 없습니다. (CPU 테스트 모드 또는 타 하드웨어 환경)"
fi

log_step "3. 서버 포트 조회 및 네트워크 방화벽 등록"

SERVER_CONFIG_FILE="$BASE_DIR/config/server_config.json"
DEFAULT_PORT=8081

if [ -f "$SERVER_CONFIG_FILE" ]; then
    PARSED_PORT=$(python3 -c "import json; print(json.load(open('$SERVER_CONFIG_FILE')).get('port', $DEFAULT_PORT))" 2>/dev/null || echo "$DEFAULT_PORT")
    SERVER_PORT=${LLAMA_PORT:-$PARSED_PORT}
else
    SERVER_PORT=${LLAMA_PORT:-$DEFAULT_PORT}
fi

log_info "서빙 포트 설정: $SERVER_PORT/tcp"

if command -v ufw &> /dev/null; then
    if sudo -n ufw status 2>/dev/null | grep -q "Status: active"; then
        log_info "ufw 방화벽 포트 $SERVER_PORT/tcp 허용 규칙 등록 중..."
        sudo -n ufw allow "$SERVER_PORT/tcp" &>/dev/null || log_warn "sudo 비밀번호 필요: 수동으로 'sudo ufw allow $SERVER_PORT/tcp' 명령을 실행하세요."
    else
        log_info "ufw 방화벽 설정 확인 완료. (포트: $SERVER_PORT/tcp)"
    fi
elif command -v firewall-cmd &> /dev/null; then
    log_info "firewalld 방화벽 포트 $SERVER_PORT/tcp 등록 확인..."
    sudo -n firewall-cmd --add-port="$SERVER_PORT/tcp" --permanent &>/dev/null || log_warn "sudo 비밀번호 필요: 수동으로 'sudo firewall-cmd --add-port=$SERVER_PORT/tcp --permanent' 실행 권장."
else
    log_info "기본 OS 방화벽 패키지(ufw/firewalld) 미감지 또는 수동 개설 권장. (포트: $SERVER_PORT/tcp)"
fi

log_step "4. 서버 구동/종료/상태 제어 쉘 스크립트 생성"

mkdir -p "$BASE_DIR/scripts"
mkdir -p "$BASE_DIR/logs"

# 4.1 start_server.sh 생성
cat << 'EOF' > "$BASE_DIR/scripts/start_server.sh"
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

nohup setsid .venv/bin/python -m src.api.server < /dev/null > "$LOG_FILE" 2>&1 &
sleep 0.5
SERVER_PID=$(pgrep -f "src.api.server" | tail -n 1 || echo "")
echo "$SERVER_PID" > "$PID_FILE"

echo -e "${COLOR_GREEN}✓ 서버 데몬 백그라운드 구동 성공! (PID: $SERVER_PID)${COLOR_NC}"

SERVER_HOST=$(uv run python -c "from src.core.config_manager import ConfigManager; print(ConfigManager().get_server_config().get('host', '127.0.0.1'))" 2>/dev/null || echo "127.0.0.1")
SERVER_PORT=$(uv run python -c "from src.core.config_manager import ConfigManager; print(ConfigManager().get_server_config().get('port', 8081))" 2>/dev/null || echo "8081")

# 서빙 준비 완료 대기 (최대 30초)
echo -n "[SERVER] 서빙 READY 상태 대기 중..."
for i in {1..30}; do
    if curl -s "http://$SERVER_HOST:$SERVER_PORT/health" > /dev/null 2>&1 || curl -s "http://$SERVER_HOST:$SERVER_PORT/v1/models" > /dev/null 2>&1; then
        echo -e "\n${COLOR_GREEN}✓ 서버 준비 완료! (http://$SERVER_HOST:$SERVER_PORT)${COLOR_NC}"
        echo -e "OpenAI API 엔드포인트: http://$SERVER_HOST:$SERVER_PORT/v1/chat/completions"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo -e "\n${COLOR_YELLOW}⚠️ 서버 초기 로딩 진행 중입니다. 로그를 확인하세요: tail -f logs/server.log${COLOR_NC}"
EOF

chmod +x "$BASE_DIR/scripts/start_server.sh"
ln -sf "$BASE_DIR/scripts/start_server.sh" "$BASE_DIR/start_server.sh"
log_info "✓ 생성 완료: scripts/start_server.sh (루트 심볼릭 링크 ./start_server.sh)"

# 4.2 stop_server.sh 생성
cat << 'EOF' > "$BASE_DIR/scripts/stop_server.sh"
#!/usr/bin/env bash
# ==============================================================================
# vllm_serv: 서빙 서버 안전 종료 및 VRAM 해제 스크립트 (stop_server.sh)
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

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

stop_pid() {
    local target_pid=$1
    if ps -p "$target_pid" > /dev/null 2>&1; then
        echo -e "${COLOR_CYAN}[STOP] vllm_serv 프로세스(PID: $target_pid) 종료 시도 중 (SIGTERM)...${COLOR_NC}"
        kill "$target_pid" 2>/dev/null || true
        for i in {1..10}; do
            if ! ps -p "$target_pid" > /dev/null 2>&1; then
                echo -e "${COLOR_GREEN}✓ 프로세스 $target_pid 정상 종료 완료.${COLOR_NC}"
                return 0
            fi
            sleep 0.5
        done
        echo -e "${COLOR_YELLOW}[STOP] 강제 종료 수행 (SIGKILL)...${COLOR_NC}"
        kill -9 "$target_pid" 2>/dev/null || true
    fi
}

if [ -f "$PID_FILE" ]; then
    SAVED_PID=$(cat "$PID_FILE")
    stop_pid "$SAVED_PID"
    rm -f "$PID_FILE"
fi

SERVER_PIDS=$(pgrep -f "src.api.server" || true)
if [ -n "$SERVER_PIDS" ]; then
    for pid in $SERVER_PIDS; do
        stop_pid "$pid"
    done
fi

# llama-server 잔여 프로세스 추가 정리
LLAMA_PIDS=$(pgrep -f "llama-server" || true)
if [ -n "$LLAMA_PIDS" ]; then
    echo -e "${COLOR_CYAN}[STOP] 잔여 llama-server 하위 프로세스 정리 중: $LLAMA_PIDS${COLOR_NC}"
    for pid in $LLAMA_PIDS; do
        kill -9 "$pid" 2>/dev/null || true
    done
fi

if command -v nvidia-smi &> /dev/null; then
    echo -e "${COLOR_GREEN}✓ VRAM 해제 상태 확인:${COLOR_NC}"
    nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
fi

echo -e "${COLOR_GREEN}✓ vllm_serv 서버 및 관련 프로세스 종료 완료.${COLOR_NC}"
EOF

chmod +x "$BASE_DIR/scripts/stop_server.sh"
ln -sf "$BASE_DIR/scripts/stop_server.sh" "$BASE_DIR/stop_server.sh"
log_info "✓ 생성 완료: scripts/stop_server.sh (루트 심볼릭 링크 ./stop_server.sh)"

# 4.3 status_server.sh 생성
cat << 'EOF' > "$BASE_DIR/scripts/status_server.sh"
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
EOF

chmod +x "$BASE_DIR/scripts/status_server.sh"
ln -sf "$BASE_DIR/scripts/status_server.sh" "$BASE_DIR/status_server.sh"
log_info "✓ 생성 완료: scripts/status_server.sh (루트 심볼릭 링크 ./status_server.sh)"

log_step "5. setup.sh 설정 완결"

log_info "vllm_serv 환경 설정 및 제어 스크립트 생성이 완료되었습니다!"
echo -e "\n사용 가능한 제어 명령어:"
echo -e "  - 서버 구동: ${COLOR_GREEN}./start_server.sh${COLOR_NC} (또는 ./scripts/start_server.sh)"
echo -e "  - 서버 종료: ${COLOR_GREEN}./stop_server.sh${COLOR_NC} (또는 ./scripts/stop_server.sh)"
echo -e "  - 상태 확인: ${COLOR_GREEN}./status_server.sh${COLOR_NC} (또는 ./scripts/status_server.sh)\n"
