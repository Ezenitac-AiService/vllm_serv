#!/usr/bin/env bash
# ==============================================================================
# vllm_serv: 공통 쉘 믹스인 스크립트 (scripts/common.sh)
# (090-audit-test-refactor)
# ==============================================================================

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

log_info() { echo -e "${COLOR_GREEN}[INFO]${COLOR_NC} $1"; }
log_warn() { echo -e "${COLOR_YELLOW}[WARN]${COLOR_NC} $1"; }
log_err()  { echo -e "${COLOR_RED}[ERROR]${COLOR_NC} $1"; }
log_step() { echo -e "\n${COLOR_CYAN}====================================================${COLOR_NC}\n${COLOR_CYAN}▶ $1${COLOR_NC}\n${COLOR_CYAN}====================================================${COLOR_NC}"; }

check_cuda_gpu_available() {
    if command -v nvidia-smi &>/dev/null && nvidia-smi -L &>/dev/null; then
        return 0
    elif [ -e /dev/nvidia0 ] || [ -d /proc/driver/nvidia ]; then
        return 0
    else
        return 1
    fi
}

get_nvidia_driver_version() {
    if command -v nvidia-smi &>/dev/null; then
        nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n 1
    elif [ -f /proc/driver/nvidia/version ]; then
        grep -oP 'NVIDIA Module\s+\K[0-9.]+' /proc/driver/nvidia/version 2>/dev/null || echo "Unknown"
    else
        echo "None"
    fi
}

get_cuda_version() {
    if command -v nvcc &>/dev/null; then
        nvcc --version 2>/dev/null | grep -oP 'release \K[0-9.]+' | head -n 1
    elif command -v nvidia-smi &>/dev/null; then
        nvidia-smi 2>/dev/null | grep -oP 'CUDA Version:\s*\K[0-9.]+' | head -n 1
    else
        echo "None"
    fi
}

get_cudnn_version() {
    local header=""
    for p in /usr/include/cudnn_version.h /usr/local/cuda/include/cudnn_version.h /usr/include/cudnn.h; do
        if [ -f "$p" ]; then
            header="$p"
            break
        fi
    done

    if [ -n "$header" ]; then
        local major=$(grep -i '#define CUDNN_MAJOR' "$header" 2>/dev/null | awk '{print $3}')
        local minor=$(grep -i '#define CUDNN_MINOR' "$header" 2>/dev/null | awk '{print $3}')
        local patch=$(grep -i '#define CUDNN_PATCHLEVEL' "$header" 2>/dev/null | awk '{print $3}')
        if [ -n "$major" ] && [ -n "$minor" ] && [ -n "$patch" ]; then
            echo "${major}.${minor}.${patch}"
            return 0
        fi
    fi
    echo "Unknown"
}

assert_cuda_gpu() {
    if ! check_cuda_gpu_available; then
        log_err "NVIDIA CUDA GPU가 장착되지 않거나 드라이버가 인식되지 않는 환경입니다."
        log_err "본 프로젝트는 CUDA GPU 전용 플랫폼 호스트만을 지원합니다. (090-audit-test-refactor)"
        exit 1
    fi
    log_info "✓ NVIDIA CUDA GPU 환경 탐지 성공 (Driver: $(get_nvidia_driver_version), CUDA: $(get_cuda_version))"
}
