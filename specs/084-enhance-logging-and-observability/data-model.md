# Data Model: 진단 로그 및 포트 바인딩 릴리스 스키마

## 1. TracebackErrorRecord (Error Log Entity)

`logs/error.log` 파일에 기록되는 스택 트레이스 엔티티 구조입니다:

```json
{
  "timestamp": "2026-08-03T05:50:00.123456+00:00",
  "client_ip": "10.0.0.41",
  "request_id": "req-0de815d3",
  "endpoint": "/v1/chat/completions",
  "status_code": 503,
  "error_type": "PortCollisionError",
  "detail_message": "Model server at port 8089 is currently unreachable or loading.",
  "target_port": 8089,
  "traceback": "Traceback (most recent call last):\n  File \"/src/api/routes/inference_api.py\", line 275...\n"
}
```

## 2. PortCleanupRecord (Port Management Entity)

`ProcessManager` 및 `stop_server.sh`가 포트 점유를 탐지 및 강제 해제할 때 사용하는 엔티티 구조입니다:

```json
{
  "target_port": 8090,
  "bound_pids": [2640501, 2640502],
  "cleanup_action": "SIGKILL",
  "is_port_released": true,
  "timestamp": "2026-08-03T05:50:00.200000+00:00"
}
```
