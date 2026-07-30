#!/usr/bin/env bash
# ==============================================================================
# vllm_serv: 타 서버 이관용 경량 Seed Pack 생성 스크립트 (make_seed_pack.sh)
# 대용량 모델 가중치(models/), 가상환경(.venv), 빌드 아티팩트(.bin/)를 배제하고
# 소스코드/설정/스크립트만 선택 패키징
# ==============================================================================

set -eo pipefail

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

log_info() { echo -e "${COLOR_GREEN}[SEED-PACK INFO]${COLOR_NC} $1"; }
log_warn() { echo -e "${COLOR_YELLOW}[SEED-PACK WARN]${COLOR_NC} $1"; }
log_err()  { echo -e "${COLOR_RED}[SEED-PACK ERROR]${COLOR_NC} $1"; }
log_step() { echo -e "\n${COLOR_CYAN}====================================================${COLOR_NC}\n${COLOR_CYAN}▶ $1${COLOR_NC}\n${COLOR_CYAN}====================================================${COLOR_NC}"; }

show_help() {
    echo "사용법: $0 [OPTIONS]"
    echo ""
    echo "vllm_serv 프로젝트의 핵심 소스코드, 설정 및 쉘 스크립트를 경량 Seed Pack 아카이브로 패키징합니다."
    echo ""
    echo "옵션:"
    echo "  -o, --output PATH       생성할 아카이브 저장 경로 지정 (기본값: dist/vllm_serv_seed.tar.gz)"
    echo "      --zip               기본 .tar.gz 대신 .zip 포맷으로 아카이브 생성"
    echo "      --build-legacy      i7-930 전용 사전 컴파일 휠(wheels/legacy_i7_930/*.whl) 번들링 (기본 활성)"
    echo "      --skip-legacy-build i7-930 전용 휠 사전 컴파일 과정 스킵"
    echo "  -h, --help              도움말 메시지 출력 후 종료"
    echo ""
    exit 0
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    BASE_DIR="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../pyproject.toml" ]; then
    BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    BASE_DIR="$(pwd)"
fi
cd "$BASE_DIR"

OUTPUT_PATH=""
USE_ZIP=0
BUILD_LEGACY=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --zip)
            USE_ZIP=1
            shift
            ;;
        --build-legacy)
            BUILD_LEGACY=1
            shift
            ;;
        --skip-legacy-build)
            BUILD_LEGACY=0
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            log_err "알 수 없는 옵션: $1"
            show_help
            ;;
    esac
done

if [ -z "$OUTPUT_PATH" ]; then
    if [ "$USE_ZIP" -eq 1 ]; then
        OUTPUT_PATH="dist/vllm_serv_seed.zip"
    else
        OUTPUT_PATH="dist/vllm_serv_seed.tar.gz"
    fi
fi

log_step "⚡ vllm_serv Seed Pack 마이그레이션 아카이브 생성"
log_info "프로젝트 루트 디렉토리: $BASE_DIR"

# 1. 필수 도구 존재 검증
if [ "$USE_ZIP" -eq 1 ]; then
    if ! command -v zip &> /dev/null; then
        log_err "'zip' 명령어를 찾을 수 없습니다. zip 패키지를 설치하거나 .tar.gz 포맷을 사용하세요."
        exit 1
    fi
    log_info "포맷 설정: ZIP (.zip)"
else
    if ! command -v tar &> /dev/null || ! command -v gzip &> /dev/null; then
        log_err "'tar' 또는 'gzip' 명령어를 찾을 수 없습니다."
        exit 1
    fi
    log_info "포맷 설정: POSIX Tarball (.tar.gz)"
fi

# 절대 경로 변환
if [[ "$OUTPUT_PATH" != /* ]]; then
    ABS_OUTPUT_PATH="$BASE_DIR/$OUTPUT_PATH"
else
    ABS_OUTPUT_PATH="$OUTPUT_PATH"
fi

OUTPUT_DIR="$(dirname "$ABS_OUTPUT_PATH")"
mkdir -p "$OUTPUT_DIR"

log_info "저장 목표 경로: $OUTPUT_PATH"
log_info "제외 항목: models/, .venv/, .bin/, logs/, build/, dist/, __pycache__/, .git/"

# 1.5 i7-930 (Nehalem) 사전 빌드 휠 검증 및 컴파일
if [ "$BUILD_LEGACY" -eq 1 ]; then
    log_info "i7-930 (Nehalem) 전용 사전 컴파일 휠 패키지 검증 수행 중..."
    mkdir -p wheels/legacy_i7_930
    EXISTING_WHEELS=$(ls wheels/legacy_i7_930/*.whl 2>/dev/null || true)
    if [ -z "$EXISTING_WHEELS" ]; then
        if command -v uv &> /dev/null; then
            log_info "i7-930 전용 휠 생성 중 (CFLAGS=-march=x86-64, sm_61 GTX1070)..."
            FORCE_CMAKE=1 \
            CFLAGS="-march=x86-64" \
            CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61" \
            uv run pip wheel "llama-cpp-python[server]" --no-binary llama-cpp-python --wheel-dir wheels/legacy_i7_930 || log_warn "i7-930 사전 휠 컴파일 실패 (온디맨드 컴파일 Fallback 적용 예정)"
        else
            log_warn "uv 패키지 매니저 미설치로 i7-930 휠 사전 컴파일 스킵 (기존 아티팩트 활용)"
        fi
    else
        log_info "✓ 기존 i7-930 사전 빌드 휠 감지됨 (wheels/legacy_i7_930/)"
    fi
fi

# 2. 아카이브 생성
if [ "$USE_ZIP" -eq 1 ]; then
    rm -f "$ABS_OUTPUT_PATH"
    zip -r -q "$ABS_OUTPUT_PATH" . \
        -x "models/*" ".venv/*" ".bin/*" "logs/*" "build/*" "dist/*" \
        "__pycache__/*" "*.pyc" "*.pyo" ".git/*" ".github/*" ".pytest_cache/*" \
        "*.tar.gz" "*.zip" "*.pid" ".coverage" "htmlcov/*"
else
    tar -czf "$ABS_OUTPUT_PATH" \
        --exclude="models" \
        --exclude=".venv" \
        --exclude=".bin" \
        --exclude="logs" \
        --exclude="build" \
        --exclude="dist" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude="*.pyo" \
        --exclude=".git" \
        --exclude=".github" \
        --exclude=".pytest_cache" \
        --exclude="*.tar.gz" \
        --exclude="*.zip" \
        --exclude="vllm_serv.pid" \
        --exclude=".coverage" \
        --exclude="htmlcov" \
        .
fi

if [ ! -f "$ABS_OUTPUT_PATH" ]; then
    log_err "Seed Pack 생성에 실패했습니다: $ABS_OUTPUT_PATH 생성되지 않음."
    exit 1
fi

SIZE_BYTES=$(stat -c%s "$ABS_OUTPUT_PATH" 2>/dev/null || stat -f%z "$ABS_OUTPUT_PATH" 2>/dev/null || echo "0")
SIZE_KB=$((SIZE_BYTES / 1024))

# 3. 필수 설정 파일 수록 검증 (config/platform_profiles.json & wheels/legacy_i7_930)
if [ "$USE_ZIP" -eq 1 ]; then
    ARCHIVE_FILES=$(unzip -l "$ABS_OUTPUT_PATH" 2>/dev/null || true)
else
    ARCHIVE_FILES=$(tar -tzf "$ABS_OUTPUT_PATH" 2>/dev/null || true)
fi

if ! echo "$ARCHIVE_FILES" | grep -q "platform_profiles.json"; then
    log_err "아카이브 검증 실패: config/platform_profiles.json 파일이 수록되지 않았습니다."
    exit 1
fi
log_info "✓ 멀티 플랫폼 설정(config/platform_profiles.json) 아카이브 수록 검증 완료"

if echo "$ARCHIVE_FILES" | grep -q "wheels/legacy_i7_930"; then
    log_info "✓ i7-930 사전 빌드 휠 디렉터리(wheels/legacy_i7_930) 아카이브 수록 검증 완료"
fi


log_info "\n[타 시스템 멀티 플랫폼 마이그레이션 안내]"
log_info "  1. 타겟 서버(예: Xeon E3 / 레거시 서버 또는 개발 머신)로 $OUTPUT_PATH 파일 이관"
if [ "$USE_ZIP" -eq 1 ]; then
    log_info "  2. unzip $OUTPUT_PATH -d vllm_serv && cd vllm_serv"
else
    log_info "  2. mkdir -p vllm_serv && tar -xzf $(basename "$OUTPUT_PATH") -C vllm_serv && cd vllm_serv"
fi
log_info "  3. ./setup.sh 실행 (하드웨어 자동 감지 & platform_profiles.json 기반 동적 CMAKE_ARGS 강제 재설치)"
log_info "  4. ./start_server.sh 실행 (사전 하드웨어 가속 점검 & 백그라운드 서빙 구동)\n"
