# Data Model: Firewall Detection & Context Benchmark Cache Schemas

## Entities

### 1. FirewallEngineProfile (방화벽 프로필 엔티티)
OS 환경에서 동작하는 네트워크 방화벽 서브시스템의 상태 및 권한 구조를 나타냅니다.

```json
{
  "system_type": "ufw | firewalld | nftables | iptables | none",
  "is_active": true,
  "permission_level": "root | sudo_passwordless | sudo_authenticated | unprivileged",
  "detection_method": "sudo_ufw_status | sudo_n_ufw_status | command_v_ufw_fallback",
  "allowed_ports": [8081, 8089]
}
```

### 2. ContextWindowProfile (컨텍스트 윈도우 스케일링 프로필 캐시 엔티티)
파일 경로: `config/model_context_profiles.json` (타겟 서버 현지 캐시 전용, 시드 팩 제외)

```json
{
  "generated_at": "2026-07-30T14:20:00Z",
  "system_hardware": {
    "gpu_name": "NVIDIA GeForce GTX 1080 Ti",
    "vram_mb": 11140,
    "system_ram_gb": 32
  },
  "profiles": {
    "qwen3.5-4b": {
      "max_context_length": 8192,
      "recommended_context_length": 4096,
      "gpu_layers": 33,
      "scaling_tested": true,
      "last_tested_at": "2026-07-30T14:20:00Z"
    },
    "llama3.2-3b": {
      "max_context_length": 16384,
      "recommended_context_length": 8192,
      "gpu_layers": 28,
      "scaling_tested": true,
      "last_tested_at": "2026-07-30T14:20:00Z"
    }
  }
}
```

### 3. BenchmarkTaskState (대시보드 재측정 백그라운드 작업 엔티티)

```json
{
  "task_id": "bench-20260730-142500",
  "status": "idle | running | completed | failed",
  "progress_percent": 65,
  "current_model": "llama3.2-3b",
  "started_at": "2026-07-30T14:25:00Z",
  "completed_at": null,
  "error_message": null
}
```
