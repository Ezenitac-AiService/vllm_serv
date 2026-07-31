# Research: start_server.sh 데몬 구동시 PYTHONPATH 예외 및 0.0.0.0 curl 바인딩 오류 수정 (067-fix-server-startup-pythonpath)

**Feature**: `067-fix-server-startup-pythonpath`

## Technical Decisions & Rationale

### Decision 1: `start_server.sh` 데몬 구동 시 `nohup setsid uv run python -m src.api.server` 적용
- **선택된 방식**: `scripts/start_server.sh`내 데몬 구동 라인을 `.venv/bin/python` 대신 `nohup setsid uv run python -m src.api.server < /dev/null > "$LOG_FILE" 2>&1 &`로 변경.
- **이유**: `uv run`은 프로젝트 루트(`/home/dev/vllm_serv`)를 `PYTHONPATH`로 자동 등록하고 가상환경 종속성을 완벽히 격리합니다. 이를 통해 `setsid` 백그라운드 구동 시 `ModuleNotFoundError: No module named 'src'`로 인한 프로세스 조기 사멸을 100% 방지합니다.

### Decision 2: `SERVER_HOST="0.0.0.0"` 바인딩 시 `CURL_HOST="127.0.0.1"` 자동 변환
- **선택된 방식**: `start_server.sh` 및 `status_server.sh`에서 파싱된 `SERVER_HOST`가 `0.0.0.0`이면 `curl` 호출용 `CURL_HOST`를 `127.0.0.1`로 대체함.
- **이유**: `0.0.0.0`은 서버 소켓 수신용 와일드카드 인터페이스 주소로, 클라이언트 `curl`이 `0.0.0.0`으로 HTTP 요청을 보낼 경우 일부 리눅스 커널/방화벽 환경에서 루프백 연결이 거부됩니다.

### Decision 3: `MetricsDB` 탑레벨 객체 생성 ➡️ 지연 싱글톤(Lazy Singleton Proxy) 전환
- **선택된 방식**: `src/core/metrics_db.py` 238번 라인의 탑레벨 `metrics_db = MetricsDB()` 구문을 `_get_metrics_db_instance()` 및 `__getattr__` 모듈 래퍼 또는 Proxy로 전환.
- **이유**: 파이썬 모듈 `import` 시점의 SQLite 디스크 커넥션 생성 및 스키마 검사를 실제 API 요청 처리 시점으로 지연시켜, 모듈 로딩 단계의 파이썬 인터프리터 사멸(`exit 1`)을 근본 차단합니다.

### Decision 4: `start_server.sh` 데몬 실패 시 Fail-Fast 진단 로그 출력
- **선택된 방식**: 헬스체크 30초 타임아웃 또는 PID 사멸 시 `logs/server.log` 하단 15줄을 콘솔에 즉시 출력하도록 개선.
- **이유**: 사용자가 무의미한 대기를 피하고 구동 실패 원인을 콘솔에서 즉시 식별할 수 있습니다.
