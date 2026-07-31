#!/usr/bin/env bash
# ==============================================================================
# vllm_serv: Seed Pack 안전 복원 및 압축 해제 스크립트 (unpack_seed.sh)
# 기존 검증 통과 유효 바이너리 덮어쓰기 방지(-k) 및 퍼미션 보존(-p) 원클릭 구동
# ==============================================================================

set -eo pipefail

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

log_info() { echo -e "${COLOR_GREEN}[UNPACK INFO]${COLOR_NC} $1"; }
log_warn() { echo -e "${COLOR_YELLOW}[UNPACK WARN]${COLOR_NC} $1"; }
log_err()  { echo -e "${COLOR_RED}[UNPACK ERROR]${COLOR_NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    BASE_DIR="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../pyproject.toml" ]; then
    BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    BASE_DIR="$(pwd)"
fi
cd "$BASE_DIR"

TAR_FILE="${1:-vllm_serv_seed.tar.gz}"

if [ ! -f "$TAR_FILE" ] && [ -f "dist/$TAR_FILE" ]; then
    TAR_FILE="dist/$TAR_FILE"
fi

if [ ! -f "$TAR_FILE" ]; then
    log_err "Seed Pack 아카이브 파일($TAR_FILE)을 찾을 수 없습니다."
    log_err "사용법: ./unpack_seed.sh [vllm_serv_seed.tar.gz]"
    exit 1
fi

log_info "⚡ vllm_serv Seed Pack 안전 압축 해제 구동"
log_info "프로젝트 루트: $BASE_DIR"
log_info "대상 아카이브: $TAR_FILE"

# Pre-check existing binaries
if uv run python scripts/verify_wheel_binary.py --check-live 2>/dev/null; then
    log_info "ℹ️ [PRESERVED] 현재 환경의 기존 바이너리가 CUDA 가속 검증을 통과했습니다."
    log_info "   압축 해제 시 기존 유효 바이너리를 덮어쓰지 않고 최우선 보존합니다 (--skip-old-files / -k)."
fi

log_info "압축 해제 실행 중 (tar -xvkpf $TAR_FILE -C ./)..."
UNPACK_ERR=0
tar -xvkpf "$TAR_FILE" -C ./ 2>/dev/null || UNPACK_ERR=$?

if [ "$UNPACK_ERR" -eq 0 ] || [ "$UNPACK_ERR" -eq 2 ]; then
    log_info "✓ Seed Pack 안전 압축 해제 완결!"
    log_info "다음 단계: ./setup.sh 실행하여 환경 및 서버 설정을 완료하세요."
else
    log_err "Seed Pack 압축 해제 중 오류가 발생했습니다 (exit code: $UNPACK_ERR)."
    exit "$UNPACK_ERR"
fi
