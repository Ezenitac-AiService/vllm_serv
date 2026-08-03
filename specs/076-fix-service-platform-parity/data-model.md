# Data Model: `076-fix-service-platform-parity`

## ServerHealthReport Entity Structure

```typescript
interface ServicePlatformHealthReport {
  detected_lan_ip: string;           // Detected primary LAN IP (e.g. 10.0.0.41 or 127.0.1.1)
  probing_target_ips: string[];      // Array of targets probed: ['127.0.0.1', 'localhost', '127.0.1.1', active_ip]
  served_models: string[];           // Array of active model IDs
  firewall_ports: {
    "8081_llm_main": boolean;        // Port 8081 socket LISTEN status
    "8082_dashboard": boolean;       // Port 8082 socket LISTEN status
  };
  api_status: {
    "/v1/models": boolean;          // HTTP 200 status
    "/health": boolean;             // HTTP 200 status
    "/v1/chat/completions": boolean;// HTTP 200 status with dict payload
  };
  dashboard_e2e_status: boolean;     // HTTP 200/307 AND HTML DOM keyword content verification
  is_healthy: boolean;               // True iff ALL ports, APIs, and DOM content pass
}
```
