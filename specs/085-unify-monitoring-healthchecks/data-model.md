# Data Model: Unified Health Probe Metric Schema

```json
{
  "timestamp": "2026-08-03T06:00:00Z",
  "lan_ip": "10.0.0.41",
  "candidate_ips": ["127.0.0.1", "localhost", "10.0.0.41"],
  "ports": {
    "8081_llm": { "status": "OPEN", "http_code": 200 },
    "8082_dashboard": { "status": "OPEN", "http_code": 200, "dom_verified": true }
  },
  "overall_status": "SYSTEM_HEALTHY"
}
```
