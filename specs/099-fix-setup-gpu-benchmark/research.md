# Research & Technical Decisions: setup.sh 폴리싱 및 GPU 모델 로드 실측 벤치마크 파이프라인 리팩토링 (099-fix-setup-gpu-benchmark)

## 1. 개요 및 기술 조사 목적

`./setup.sh --force-benchmark` 구동 시 백그라운드 `llama-server` 백엔드 프로세스의 GPU 레이어 오프로딩(`-ngl 99`) 스폰 실패, 포트 충돌, 또는 웜업 추론 요청 타임아웃/실패로 인해 **nvtop 상에서 VRAM 할당 및 GPU 로드가 전혀 발생하지 않고 모든 모델이 TPS: 0.0, Supported: False 처리되는 현상**을 근본 해결하기 위해 조사한 아키텍처 및 기술 결정 사항을 수록합니다.

---

## 2. 핵심 기술 결정 (Technical Decisions)

### Decision 1: 원자적 사전 서버 종료 (Pre-Execution Cleanup)
- **선택된 방안**: `setup.sh` 환경 구축 초기 단계(Step 0 또는 Step 1)에서 기존 가동 중인 `llama-server` 백엔드 프로세스 및 FastAPI 서빙 프로세스를 자동으로 감지하여 원자적으로 안전 종료(`stop_server.sh` 호출 또는 `ProcessManager` 포트 점유 프로세스 종료)시킨 후 Clean 상태에서 포트 바인딩 및 GPU 벤치마크를 수행.
- **채택 사유**: 기존 서빙 프로세스나 좀비 프로세스가 8081 포트를 점유하고 있으면 벤치마크용 `llama-server` 스폰이 포트 바인딩 실패로 무소음 종료되므로, 스업 시작 시 포트를 100% 비워 결함을 사전 차단.
- **기각된 대안**: 포트가 점유된 상태에서 임의의 빈 포트(e.g., 8099, 8100)로 동적 변경 시도 — 대시보드 및 기존 설정 포트 모니터링과의 불일치 발생으로 기각.

---

### Decision 2: `/health` 엔드포인트 비동기 Polling 기반 Ready 검증
- **선택된 방안**: `llama-server` 프로세스 스폰 직후 `httpx.AsyncClient`를 사용하여 `http://127.0.0.1:8081/health` 엔드포인트를 0.2초 간격으로 최대 10초간 비동기 Polling하여 HTTP 200 OK (`{"status": "ok"}`) 수신 즉시 `/v1/chat/completions` 웜업 인퍼런스 요청을 전송.
- **채택 사유**: 고정 대기시간(`asyncio.sleep(0.5)`) 사용 시 모델 크기(4B/9B)에 따른 VRAM 가중치 로딩 시간 차이로 인해 Race Condition이 발생하여 `Connection Refused` 또는 503 오류가 발생함. Polling을 도입하여 Ready 상태에 도달한 시점에 정확히 웜업 추론을 수행함으로써 100% 안정성을 확보.
- **기각된 대안**: 단순 고정 대기시간(`sleep(3.0)`) — 소형 모델은 무필요하게 대기하고 대형 모델은 3초로도 부족하여 거부됨.

---

### Decision 3: 시그널 및 atexit 자율 회수 데몬 (Self-Cleanup Daemon)
- **선택된 방안**: Python `signal` 핸들러(`SIGINT`, `SIGTERM`) 및 `atexit` 훅에 `ProcessManager.force_kill_zombie_llama_servers()`를 등록.
- **채택 사유**: 벤치마크 수행 중 사용자가 `Ctrl+C`로 중단하거나 예외가 발생하더라도 백그라운드에 남아있을 수 있는 임시 `llama-server` 백그라운드 프로세스와 점유 포트를 100% 자동 해제.
- **기각된 대안**: `try...finally` 블록만 사용 — SIGKILL 또는 시그널 중단 시 `finally` 블록이 실행되지 않아 좀비 프로세스가 남음.

---

### Decision 4: 루프백 전용 바인딩 (`--host 127.0.0.1`) 보안 격리
- **선택된 방안**: `ProcessManager.spawn_process()`에서 `llama-server` 백엔드 가동 명령 인자로 `--host 127.0.0.1` 및 `-ngl 99`를 명시적으로 전달.
- **채택 사유**: 벤치마크용 임시 백엔드가 외부 인터페이스(`0.0.0.0`)로 노출되는 보안 위험을 방지하고 로컬 루프백 인터페이스로 완전 격리.

---

### Decision 5: setup.sh 이중 강제 벤치마크 제거 및 스마트 스킵
- **선택된 방안**: `setup.sh` 지정 시 Step 2.8에서 전체 카탈로그 벤치마크 및 `config/model_context_profiles.json` 프로필 생성을 완납하면, Step 4.5에서는 프로필 완비 상태를 확인하여 5초 이내 고속 스킵(Smart Skip).
- **채택 사유**: 기존에는 `--force-benchmark` 지정 시 Step 2.8과 Step 4.5에서 6개 모델 벤치마크를 2회 연속 중복 호출하여 대기시간이 2배 소모되었음. 중복 호출을 제거하여 40% 이상 구동 시간 단축.

---

### Decision 6: setup.sh 완수 후 서빙 자동 복구 (Auto-Restore)
- **선택된 방안**: `setup.sh` 최종 완료 단계(Step 5)에서 벤치마크 결과 선정된 최적 모델과 추천 컨텍스트 윈도우 크기로 `./start_server.sh`를 자동 호출하고 서빙 헬스체크 완수.
- **채택 사유**: 사전 정리(FR-006)로 기존 서버가 정지된 후 환경 구축이 끝나면 즉시 서비스를 복구하여 다운타임 최소화 및 시스템 사용성 보장.

---

### Decision 7: OOM / 타임아웃 / 가중치 미비 명확한 Fallback 및 경고 로그
- **선택된 방안**: OOM, 120초 타임아웃, 로컬 `.gguf` 파일 미비 발생 시 터미널에 `[BENCHMARK WARN]` 상세 원인을 출력하고, `model_context_profiles.json`에 `is_supported=false`, `recommended_context_length=2048`, `scaling_tested=false`로 기록 후 파이프라인 지속.
- **채택 사유**: 일부 대형 모델의 OOM 실패가 전체 스크립트를 중단시키지 않고 파이프라인을 비파괴적으로 완료하도록 보장.
