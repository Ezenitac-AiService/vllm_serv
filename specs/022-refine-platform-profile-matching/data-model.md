# Data Model & Configuration Schemas: 플랫폼 프로필 매칭 정교화

## 1. Platform Profile JSON Schema (`config/platform_profiles.json`)

```json
{
  "legacy-i7-930-gtx1070": {
    "profile_id": "legacy-i7-930-gtx1070",
    "name": "Legacy Nehalem i7-930 + GTX 1070 Server",
    "cpu_model": "Intel(R) Core(TM) i7 CPU 930 @ 2.80GHz",
    "ram_gb": 24,
    "gpu_name": "NVIDIA GeForce GTX 1070",
    "vram_mb": 8192,
    "compute_capability": "6.1",
    "os_name": "Ubuntu Server 24.04 LTS",
    "expected_avx": false,
    "expected_avx2": false
  },
  "pascal-avx2-gtx1080ti": {
    "profile_id": "pascal-avx2-gtx1080ti",
    "name": "Haswell Xeon E3-1231 v3 + GTX 1080 Ti Server",
    "cpu_model": "Intel(R) Xeon(R) CPU E3-1231 v3 @ 3.40GHz",
    "ram_gb": 32,
    "gpu_name": "NVIDIA GeForce GTX 1080 Ti",
    "vram_mb": 11264,
    "compute_capability": "6.1",
    "os_name": "Ubuntu Server 24.04 LTS",
    "expected_avx": true,
    "expected_avx2": true
  },
  "dev-rtx3060": {
    "profile_id": "dev-rtx3060",
    "name": "Modern Workstation (RTX 3060)",
    "cpu_model": "Modern x86_64 CPU (AVX2/FMA)",
    "ram_gb": 32,
    "gpu_name": "NVIDIA GeForce RTX 3060",
    "vram_mb": 12288,
    "compute_capability": "8.6",
    "os_name": "Linux x86_64",
    "expected_avx": true,
    "expected_avx2": true
  }
}
```

## 2. Pydantic Entity Class Update (`TargetPlatformProfile`)

`src/core/cpu_detector.py` 내 Pydantic 모델 업데이트:

```python
class TargetPlatformProfile(BaseModel):
    """Hardware Profile Entity."""
    profile_id: str
    name: str
    cpu_model: str
    ram_gb: int
    gpu_name: str
    vram_mb: int
    compute_capability: str
    os_name: str
    expected_avx: bool
    expected_avx2: bool = True
```
