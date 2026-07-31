# Research: llama.cpp 기반 벤치마크 및 모델 전환 전략

## Decision 1: llama.cpp 연동 방식
- **Decision**: Python 기반 `llama-cpp-python` 라이브러리를 사용하며, FastAPI 기반의 자체 래퍼(Wrapper) 스크립트를 작성하여 모델 로드/언로드를 제어합니다.
- **Rationale**: `llama_cpp.server` 기본 모듈은 단일 프로세스에서 서버 시작 시 모델을 로드합니다. 런타임에 2B/4B/12B 모델을 API로 동적으로 전환(로드/언로드)하려면 `Llama` 인스턴스를 관리할 수 있는 사용자 정의 FastAPI 서버가 필요합니다.
- **Alternatives considered**: Bash 스크립트로 `llama_cpp.server` 프로세스를 kill하고 재시작하는 방식. 구현은 단순하나, HTTP API를 통해 "동적 전환"을 제공하라는 요구사항(FR-006)에는 FastAPI 래퍼 구조가 더 적합함.

## Decision 2: 벤치마크 자동화 도구
- **Decision**: 별도의 Python 스크립트(`benchmark.py`)를 통해 허깅페이스에서 2B, 4B, 12B GGUF 파일을 다운로드하고, 각각 `Llama` 인스턴스로 로드하여 토큰 생성 시간(TPOT)과 VRAM 점유율(CUDA memory tracking)을 실측합니다.
- **Rationale**: 배포 전 벤치마크를 통해 GTX 1080 Ti의 11GB 한계를 명확히 평가해야 하므로, 동일한 프롬프트로 세 모델을 순차적으로 테스트하는 독립적인 스크립트가 필요합니다.
- **Alternatives considered**: 외부 부하 테스트 툴(K6, JMeter) 사용. 단일 사용자 최적화 및 VRAM 실측을 위해서는 Python 스크립트 내부 측정(pynvml 등)이 더 직관적임.

## Decision 3: 컨텍스트 길이 (Context Window) 제어
- **Decision**: `n_ctx=4096` 파라미터를 하드코딩 혹은 기본 환경 변수로 강제 적용합니다.
- **Rationale**: 명세서(Spec)에 단일 사용자 접속 시 OOM 방지를 위해 최대 4K 컨텍스트로 제한하기로 명시되었습니다.
