# Data Model & Flow Architecture: Fast-Track 휠 검증 서브쉘 종료 코드 캡처 구문 수정 및 C++ 소스 재컴파일 Fallback 정상 전이 보장 (056-fix-subshell-status-code-fallback)

## 1. 3중 방어선 스크립트 실행 플로우차트 (3-Tier Script Defense Flowchart)

```mermaid
flowchart TD
    Start[./setup.sh 실행] --> Step0[Step 0: Sudo 및 기본 파일 검증]
    Step0 --> Step1[Step 1: uv 가상환경 동기화]
    Step1 --> Step2[Step 2: 4단계 휠 복원 & 3중 하드웨어 검증]

    subgraph TieredResolution [Step 2: 4단계 결정론적 휠 복원]
        T1[Tier 1: --wheel-path 휠] --> T1Check{GPU 검증 성공?}
        T1Check -- Exit 0 --> T1Pass[INSTALLED_VIA_FAST_TRACK=1]
        T1Check -- Exit !=0 --> T2[Tier 2: .venv 현지 패키지 검증]
        
        T2 -- True --> T2Pass[INSTALLED_VIA_FAST_TRACK=1]
        T2 -- False --> T3[Tier 3: Seed Pack 번들 사전 빌드 휠]

        T3 --> SubshellCheck["GPU_CHECK_OUTPUT=$(uv run python...) || GPU_CHECK_STATUS=$?"]
        SubshellCheck --> ExitCodeCheck{GPU_CHECK_STATUS == 0?}
        
        ExitCodeCheck -- Yes --> T3Pass[INSTALLED_VIA_FAST_TRACK=1]
        ExitCodeCheck -- No (Exit 2/132) --> Uninstall[Clean Step: uv pip uninstall llama-cpp-python]
        Uninstall --> T4[Tier 4: C++ 동적 소스 재컴파일 Fallback]
        T4 --> T4Check{C++ 빌드 GPU 검증 성공?}
        T4Check -- Yes --> Pass[설치 완결]
        T4Check -- No --> Abort[setup.sh 즉시 중단 exit 1]
    end

    Pass --> SymlinkStep[Step 4: 루트 제어 심볼릭 링크 생성]
    SymlinkStep --> StartServer[./start_server.sh 구동]

    subgraph StartServerPreflight [start_server.sh 2중 방어선]
        StartServer --> Preflight[check_hardware_preflight]
        Preflight --> CheckLlama{llama_supports_gpu_offload == True?}
        CheckLlama -- Yes --> Daemon[서버 데몬 백그라운드 구동]
        CheckLlama -- No --> FailFast[Fail-Fast: 서버 구동 차단 exit 1]
    end

    Daemon --> StatusServer[./status_server.sh 실측 점검]
    StatusServer --> Report[llama-cpp-python GPU: ✓ CUDA 가속 활성 리포트]
```

---

## 2. 서브쉘 상태 데이터 구조 (Subshell Verification Status Schema)

| 변수명 / 필드명 | 데이터 타입 | 설명 | 허용 값 범위 및 예시 |
|-----------------|-------------|------|----------------------|
| `GPU_CHECK_OUTPUT` | `string` | 서브쉘 `uv run python` 구문 실행 시 stdout 및 stderr 출력 트레이스백 | 예: `"ERROR: llama_supports_gpu_offload() returned False"` |
| `GPU_CHECK_STATUS` | `integer` | 서브쉘 명령의 실제 exit status code (`$?`) | `0` (성공), `2` (GPU 오프로드 실패), `132` (SIGILL AVX 유입) |
| `INSTALLED_VIA_FAST_TRACK` | `integer` | Fast-Track 사전 휠 복원 성공 여부 플래그 | `1` (Fast-Track 성공), `0` (Fallback 필요) |
| `preflight.passed` | `boolean` | `check_hardware_preflight()` 전체 검증 결과 | `True` / `False` |
| `preflight.llama_gpu_offload` | `boolean` | `.venv` 내 `llama-cpp-python` CUDA 가속 기능 활성화 여부 | `True` / `False` |
