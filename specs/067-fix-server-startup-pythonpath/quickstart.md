# Quickstart & End-to-End Validation Guide: start_server.sh 데몬 구동 수정 (067-fix-server-startup-pythonpath)

**Feature**: `067-fix-server-startup-pythonpath`

## 1. 검증 시나리오 1: 데몬 스크립트 실행 및 상태 확인
```bash
# 1. 서버 구동
./start_server.sh

# 2. 서버 상태 및 PID 조회
./status_server.sh

# 3. 서버 정상 종료
./stop_server.sh
```
**기대 결과**:
- `./start_server.sh` 구동 시 `✓ 서버 데몬 백그라운드 구동 성공!` 및 `✓ 서버 준비 완료!` 출력
- `./status_server.sh` 조회 시 `프로세스 상태: 🟢 구동 중 (RUNNING)` 100% 유지

---

## 2. 검증 시나리오 2: 자동화 테스트 수트 검증
```bash
uv run pytest tests/unit/test_seed_pack_legacy.py
uv run pytest
```
**기대 결과**: 100% Green Pass 통과
