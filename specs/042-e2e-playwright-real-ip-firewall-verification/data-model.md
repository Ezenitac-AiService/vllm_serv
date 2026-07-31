# Data Model: Playwright E2E & Network Binding Entities

## Entities

### 1. NetworkBindingConfig (네트워크 바인딩 엔티티)

```json
{
  "host": "0.0.0.0",
  "port": 8089,
  "service_name": "vllm_serv Dashboard API",
  "external_access_url": "http://10.0.0.41:8089/dashboard"
}
```

### 2. PlaywrightTestResult (Playwright 실측 결과 엔티티)

```json
{
  "target_url": "http://10.0.0.41:8089/dashboard",
  "http_status_code": 200,
  "page_title": "vllm_serv Qwen3.5 & Gemma4 GPU Serving Dashboard",
  "dom_elements_rendered": true,
  "screen_captured": true
}
```
