# Quickstart Validation Guide: `README.md` 프로젝트 설명, 셋업 파이프라인, 제어 쉘 명령 및 수동 스크립트 가이드 고도화 명세 (103-readme-documentation-enhancement)

본 가이드는 `README.md` 문서에 포함될 셋업 파이프라인, 상태 제어 쉘 명령, 수동 스크립트 실행 예시 및 CLI 파라미터 레퍼런스의 실측 작동 정합성을 검증하는 시나리오를 제공합니다.

---

## 1. Prerequisites

- Linux (Ubuntu 22.04 LTS) / Bash 쉘 환경
- `uv` 패키지 관리자 환경
- 프로젝트 최상위 디렉토리 `/home/dev/storage/vllm_serv`

---

## 2. Validation Scenarios

### Scenario A: 원스톱 셋업 쉘 스크립트 및 9단계 파이프라인 검증
`./setup.sh` 구동 및 옵션 플래그가 정상 작동하는지 수동 검증합니다:

```bash
# 옵션 플래그 검증 (3단계 실측 벤치마크 스킵 고속 가동)
./setup.sh --skip-benchmark
```
- **Expected Outcome**: 관리자 권한 확보, `uv sync`, CUDA 드라이버 검증, 방화벽 개방 및 제어 스크립트가 생성되고 기존 `server_config.json` 설정을 유지하며 정상 종료됨.

---

### Scenario B: 서버 상태 변경 쉘 명령 검증 (시작, 종료, 상태확인)
서버 백그라운드 구동, 헬스체크 및 안전 종료 쉘 명령을 검증합니다:

```bash
# 1. 서버 백그라운드 시작
./start_server.sh

# 2. 서버 헬스체크 및 VRAM 상태 확인
./status_server.sh

# 3. 서버 안전 종료 및 VRAM 메모리 해제
./stop_server.sh
```
- **Expected Outcome**:
  - `start_server.sh`: 백그라운드 데몬 구동 및 100% VRAM 오프로드 후 `READY` 상태 전환.
  - `status_server.sh`: 서빙 PID, HTTP `/health` JSON 및 nvidia-smi VRAM 현황 리포트.
  - `stop_server.sh`: 안전한 SIGTERM/SIGKILL 및 VRAM 메모리 100% 반납.

---

### Scenario C: 카탈로그 다운로드 헬퍼 수동 실행 검증 (`scripts/ensure_models.py`)
카탈로그 모델 점검 CLI 플래그를 검증합니다:

```bash
# 전체 14개 모델 점검
uv run scripts/ensure_models.py --all --check-only

# 특정 모델 핀포인트 점검
uv run scripts/ensure_models.py --model qwen3.6-27b --check-only
```
- **Expected Outcome**: 카탈로그 모델 존재 유무 정밀 리포트.

---

### Scenario D: SpecKit 기능 명세 스크립트 수동 실행 검증 (`create-new-feature.sh`)
명세 생성 CLI 스크립트의 스마트 슬러그 추출 및 순차 번호 생성을 검증합니다:

```bash
# dry-run 예시
.specify/scripts/bash/create-new-feature.sh --dry-run --short-name "readme-enhancement-guide" "README.md 문서 고도화 명세"
```
- **Expected Outcome**: `specs/103-readme-enhancement-guide` 또는 지정 디렉터리 경로 계산 결과 반환.

---

## 3. Unit Test Suite Validation

프로젝트 단위 테스트 수트를 가동하여 회귀 파손 여부를 확인합니다:

```bash
uv run pytest tests/unit/
```
