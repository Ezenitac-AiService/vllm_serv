# Research Document: 멀티 플랫폼 하드웨어 사양(16GB RAM) 및 서브넷 네트워크 토폴로지(10.0.0.x vs 192.168.0.x) 보정 (028-update-platform-network-profiles)

## Decision 1: 하드웨어 사양 정정 및 네트워크 서브넷 대역격리 수립

### Decision
- `config/platform_profiles.json` 내 `dev-rtx3060` (Platform B) 프로필의 `ram_gb` 수치를 32GB에서 **16GB**로 변경.
- 네트워크 토폴로지 격리 반영:
  - Platform A (`pascal-avx2-gtx1080ti`, 개발망): `allowed_subnets: ["127.0.0.1", "10.0.0.0/8"]`
  - Platform B (`dev-rtx3060`, 훈련생망): `allowed_subnets: ["127.0.0.1", "192.168.0.0/16"]`
  - Platform C (`legacy-i7-930-gtx1070`, 서비스망): `allowed_subnets: ["127.0.0.1", "192.168.0.0/16"]`

### Rationale
- 실제 훈련생 팀 프로젝트용 서버(Platform B)는 16GB 물리 RAM이 탑재된 장비이므로 설정 파일과 인지 로직의 32GB 표기를 수정해야 오탐 및 불일치를 방지할 수 있습니다.
- 개발 환경(Platform A: `10.0.0.x`)과 훈련/서비스 환경(Platform B/C: `192.168.0.x`)을 IP CIDR 서브넷 수준에서 구분하여 인가받지 않은 네트워크 영역으로부터의 API 호출을 차단합니다.

### Alternatives Considered
- 전체 동일 서브넷(`0.0.0.0/0` 또는 모든 CIDR 허용): 보안 격리가 파기되므로 기각.

---

## Decision 2: `server_config.json` static VRAM 하드코딩 제거 및 동적 VRAM 바인딩

### Decision
- `config/server_config.json` 파일에서 기존 `vram_max_capacity_mb: 11264` 고정 하드코딩 항목 제거 (또는 None/동적 감지 기본값으로 변경).
- `ConfigManager` 및 GPU 감지 모듈(`GPUManager`/`NVML`)을 연동하여, 실제 장치 감지 시:
  1. NVML 런타임 쿼리 VRAM (예: RTX 3060 12,288 MB, GTX 1080 Ti 11,264 MB, GTX 1070 8,192 MB)
  2. NVML 미지원/실패 시 `platform_profiles.json` 내 매칭 프로필의 `vram_mb` 로드.

### Rationale
- GTX 1070 (8GB) 환경에서 11264MB 고정값을 참조할 경우 VRAM 용량 초과 산출로 인한 OOM 방지 예측 오차가 발생하고, RTX 3060 (12GB) 환경에서는 남은 1GB VRAM을 활용하지 못하는 문제가 발생합니다.

---

## Decision 3: 관리자 암호(`admin_secret`) 명시화 및 12-Factor 오버라이드 지원

### Decision
- `config/server_config.json`에 아래 필드 명시 추가:
  ```json
  {
    "admin_secret": "aiservice",
    "api_key_enabled": false,
    "api_keys": []
  }
  ```
- `ConfigManager.get_server_config()`에서 환경변수 `VLLM_ADMIN_SECRET`을 우선 확인하고, 존재할 경우 `admin_secret`을 해당 값으로 오버라이드합니다.

### Rationale
- 실습/훈련 환경에서는 JSON 설정으로 즉시 기본 암호(`aiservice`)를 파악할 수 있도록 편의성을 제공하고, 배포 및 운영 환경에서는 환경변수 지정을 통해 12-Factor App 보안 규칙을 준수합니다.

---

## Decision 4: 컨텍스트 윈도우 스케일링 동적 제어 및 초과 시 HTTP 400 에러 응답

### Decision
- `config/model_catalog.json` 내 각 모델별 `default_n_ctx` (기본 4096) 및 소형/대형 모델 구분 정의:
  - 소형 모델 (`gemma4-e2b`, `qwen3.5-2b`, `qwen3.5-4b`): VRAM 가여유분 감지/실측 벤치마크 결과에 따라 8,192~16,384 (8K~16K) 컨텍스트 확장 허용.
  - 대형 모델 (`gemma4-12b`, `qwen3.5-9b`): VRAM OOM 방지를 위하여 동적 상한 max_n_ctx = 4,096 (4K) 고정.
- 클라이언트가 요청한 `n_ctx` (또는 prompt_tokens + max_tokens)가 해당 모델/장비의 `max_n_ctx`를 초과하는 경우:
  - OpenAI 규격 HTTP 400 Bad Request 에러 반환:
    ```json
    {
      "error": {
        "message": "Requested context length (8192) exceeds model maximum allowed context length (4096) for model gemma4-12b.",
        "type": "invalid_request_error",
        "param": "n_ctx",
        "code": "context_length_exceeded"
      }
    }
    ```

### Rationale
- 대형 모델의 무분별한 컨텍스트 확장은 VRAM OOM으로 서버 전체를 다운시킬 수 있으므로 런타임 진입 시 HTTP 400으로 명확한 오류 원인과 허용 최대치를 전달합니다.

---

## Decision 5: `setup.sh` 구축 파이프라인 Non-blocking 벤치마크 & Fallback 연동

### Decision
- `scripts/setup.sh` 실행 마지막 단계에서 `src/scripts/benchmark_context_scaling.py`를 백그라운드/Non-blocking으로 1회 실행하여 결과를 `config/model_context_profiles.json` 파일로 생성/캐싱.
- 벤치마크 실패 트랩 구현:
  ```bash
  uv run python -m src.scripts.benchmark_context_scaling || log_warn "Context benchmark skipped, relying on estimate_kv_cache_vram()"
  ```
- 서버 시작 시:
  1. `config/model_context_profiles.json` 캐시 파일이 존재하면 0ms 속도로 로드.
  2. 미존재 시 `estimate_kv_cache_vram()`으로 안전 계산 진행.
- 관리자 온디맨드 API `POST /v1/admin/benchmark/run` 구현으로 런타임 중 재측정 지원.

### Rationale
- 구축 파이프라인에서 GPU 벤치마크 실패가 전체 서버 설치를 블로킹하지 않도록 보장하여 시스템 안정성을 극대화합니다.
