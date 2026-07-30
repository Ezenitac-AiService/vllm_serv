# Quickstart Guide: i7-930 사전 빌드 휠 매칭 및 오프라인 Fast-Track 검증 (030-fix-legacy-wheel-selection)

## 사전 준비 사항 (Prerequisites)

1. Python 3.12 및 `uv` 환경 구축
2. `wheels/legacy_i7_930/` 디렉터리에 타 패키지 휠(`annotated_doc-*.whl` 등)과 `llama_cpp_python-*.whl`이 공존하는 테스트 환경

## 검증 시나리오 1: 다종 휠 공존 시 llama_cpp_python 정밀 매칭 및 Fast-Track 복원 검증

```bash
# 1. 휠 디렉터리에 타 패키지 휠과 llama_cpp_python 휠 공존 상태 확인
ls -la wheels/legacy_i7_930/

# 2. setup.sh 실행 (i7-930 프로필 감지 환경)
./scripts/setup.sh

# 3. 로그 출력에서 annotated_doc이 아닌 llama_cpp_python 휠이 선택되었는지 확인
# [SETUP INFO] ⚡ i7-930 타겟 플랫폼 감지! 사전 빌드 휠(wheels/legacy_i7_930/llama_cpp_python-0.3.34-...) Fast-Track 복원을 시작합니다.
# [SETUP INFO] ✓ i7-930 사전 빌드 휠 Fast-Track 설치 완료
# [SETUP INFO] ✓ CUDA GPU 가속 활성화 확인 완료
```

## 검증 시나리오 2: 휠 유실 또는 GPU 검증 실패 시 소스 컴파일 Fallback 검증

```bash
# 1. 임시 휠 백업 및 llama_cpp_python 휠 제거
mv wheels/legacy_i7_930/llama_cpp_python*.whl /tmp/ 2>/dev/null || true

# 2. setup.sh 실행
./scripts/setup.sh

# 3. 경고 로그 출력 후 소스 컴파일 Fallback 수행 확인
# [SETUP WARN] ⚠️ i7-930 사전 빌드 휠(wheels/legacy_i7_930/llama_cpp_python*.whl)이 존재하지 않습니다.
# [SETUP WARN] 기존 C++ 소스 컴파일 파이프라인으로 Fallback합니다.

# 4. 테스트 완료 후 휠 원복
mv /tmp/llama_cpp_python*.whl wheels/legacy_i7_930/ 2>/dev/null || true
```

## 검증 시나리오 3: Pytest 단위 테스트 수트 실행

```bash
# i7-930 시드 팩 및 휠 복원 테스트 실행
uv run pytest tests/unit/test_seed_pack_legacy.py
```
