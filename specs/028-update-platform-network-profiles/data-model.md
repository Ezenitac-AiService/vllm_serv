# Data Model: 멀티 플랫폼 하드웨어 사양 및 서브넷 네트워크 토폴로지 보정 (028-update-platform-network-profiles)

## Entities & Data Schemas

### 1. PlatformProfile (`config/platform_profiles.json`)

하드웨어 스펙 및 네트워크 인가 서브넷 정의 엔티티.

```json
{
  "dev-rtx3060": {
    "profile_id": "dev-rtx3060",
    "name": "Primary Trainee Development Workstation (i7-4770 / RTX 3060)",
    "cpu_model": "Modern x86_64 CPU / i7-4770",
    "ram_gb": 16,
    "gpu_name": "NVIDIA GeForce RTX 3060",
    "vram_mb": 12288,
    "compute_capability": "8.6",
    "os_name": "Linux x86_64",
    "expected_avx": true,
    "expected_avx2": true,
    "network": {
      "bind_host": "0.0.0.0",
      "allowed_subnets": ["127.0.0.1", "192.168.0.0/16"],
      "firewall_auto_allow": true
    }
  },
  "pascal-avx2-gtx1080ti": {
    "profile_id": "pascal-avx2-gtx1080ti",
    "name": "Haswell Xeon E3-1231 v3 + GTX 1080 Ti Development Server",
    "cpu_model": "Intel(R) Xeon(R) CPU E3-1231 v3 @ 3.40GHz",
    "ram_gb": 32,
    "gpu_name": "NVIDIA GeForce GTX 1080 Ti",
    "vram_mb": 11264,
    "compute_capability": "6.1",
    "os_name": "Ubuntu Server 24.04 LTS",
    "expected_avx": true,
    "expected_avx2": true,
    "network": {
      "bind_host": "0.0.0.0",
      "allowed_subnets": ["127.0.0.1", "10.0.0.0/8"],
      "firewall_auto_allow": true
    }
  },
  "legacy-i7-930-gtx1070": {
    "profile_id": "legacy-i7-930-gtx1070",
    "name": "Legacy Trainee Service Server (i7 930 + GTX 1070)",
    "cpu_model": "Intel Core i7 930 @ 2.80GHz",
    "ram_gb": 24,
    "gpu_name": "NVIDIA GeForce GTX 1070",
    "vram_mb": 8192,
    "compute_capability": "6.1",
    "os_name": "Ubuntu Server 24.04 LTS",
    "expected_avx": false,
    "expected_avx2": false,
    "network": {
      "bind_host": "0.0.0.0",
      "allowed_subnets": ["127.0.0.1", "192.168.0.0/16"],
      "firewall_auto_allow": true
    }
  }
}
```

**Validation Rules**:
- `dev-rtx3060.ram_gb`는 정확히 `16`이어야 합니다 (기존 32에서 정정).
- `pascal-avx2-gtx1080ti.network.allowed_subnets`에 `10.0.0.0/8` 포함 필수.
- `dev-rtx3060.network.allowed_subnets` 및 `legacy-i7-930-gtx1070.network.allowed_subnets`에 `192.168.0.0/16` 포함 필수.

---

### 2. ServerConfig (`config/server_config.json`)

서버 전역 설정 및 관리자 보안 엔티티.

```json
{
  "port": 8081,
  "backend_port": 8089,
  "host": "0.0.0.0",
  "firewall_auto_allow": true,
  "healthcheck_timeout_s": 120,
  "connection_pool": {
    "max_keepalive_connections": 20,
    "max_connections": 100
  },
  "vram_max_capacity_mb": null,
  "graceful_drain_timeout_s": 5.0,
  "admin_secret": "aiservice",
  "api_key_enabled": false,
  "api_keys": [],
  "speculative_decoding": {
    "enabled": false,
    "draft_model": "qwen3.5-2b"
  },
  "structured_output": {
    "enabled": true,
    "strict_json_schema": true
  }
}
```

**Validation & State Rules**:
- `vram_max_capacity_mb`: Static 11264 하드코딩 제거. `null` 또는 미지정 시 런타임 NVML query / `platform_profiles.json` 기반 동적 주입.
- `admin_secret`: 기본값 `"aiservice"`. 환경변수 `VLLM_ADMIN_SECRET` 감지 시 우선 적용.

---

### 3. ModelContextProfileCache (`config/model_context_profiles.json`)

컨텍스트 윈도우 스케일링 측정 캐시 엔티티.

```json
{
  "gemma4-e2b": {
    "model_id": "gemma4-e2b",
    "max_safe_n_ctx": 16384,
    "peak_vram_mb": 4200,
    "status": "SUCCESS",
    "measured_at": "2026-07-30T07:00:00Z"
  },
  "gemma4-12b": {
    "model_id": "gemma4-12b",
    "max_safe_n_ctx": 4096,
    "peak_vram_mb": 11500,
    "status": "CAP_APPLIED",
    "measured_at": "2026-07-30T07:00:00Z"
  }
}
```

**State Transitions**:
- 미측정 상태 -> `setup.sh` 또는 `POST /v1/admin/benchmark/run` 수행 -> `config/model_context_profiles.json` 생성 및 갱신 -> 서버 런타임 0ms 로드.
- 측정 실패 시 -> non-blocking fallback -> `estimate_kv_cache_vram()` 동적 계산.
