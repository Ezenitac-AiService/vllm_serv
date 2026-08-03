# Domain Data Model & Diagnostics Schema: 075-fix-server-health-diagnostics

## 1. Health Status Data Structure

`scripts/diagnose_server_health.py` 진단 결과 파싱 엔티티 구조입니다.

```text
HealthReport
├── lan_ip: str                   # 예: "127.0.1.1" 또는 "192.168.0.100"
├── serving_models: List[str]     # ["gemma4-e2b", "qwen3.5-4b", "bge-m3", ...]
├── ports: Dict[str, PortStatus]
│   ├── 8081_llm_main: PortStatus(port=8081, open=True, name="llm_main")
│   └── 8082_dashboard: PortStatus(port=8082, open=True, name="dashboard")
├── endpoints: Dict[str, EndpointStatus]
│   ├── /v1/models: EndpointStatus(path="/v1/models", status_code=200, status="OK")
│   ├── /health: EndpointStatus(path="/health", status_code=200, status="OK")
│   └── /v1/chat/completions: EndpointStatus(path="/v1/chat/completions", status_code=200, status="OK")
├── dashboard_rendering: bool     # True (ON) / False (OFF)
└── overall_status: str           # "SYSTEM HEALTHY"
```

## 2. Process & Port Lifecycle Binding

```text
start_server.sh
├── [PID A] llama-server (Port 8081 - qwen3.5-4b)
├── [PID B] llama-server (Port 8090 - bge-m3)
├── [PID C] llama-server (Port 8091 - bge-reranker-v2-m3)
├── [PID D] vllm_serv REST API Gateway (Port 8081 Uvicorn)
└── [PID E] vllm_serv Web Dashboard UI (Port 8082 Uvicorn/FastAPI)
```
