# Quickstart: Validation & Verification Guide

Feature `040-ufw-sudo-detection-fix` 검증을 위한 종합 실측 실행 명령어 및 가이드입니다.

---

## 1. UFW Sudo 권한 오감지 방지 검증 (Anti-Mock Real Verification)

```bash
# 1. 일반 계정 환경에서 setup.sh 구동 시 sudo ufw status 정상 인식 실측
./scripts/setup.sh

# Expected Output:
# [SETUP INFO] 서빙 포트 설정: 8081/tcp
# [SETUP INFO] ufw 방화벽 감지. 서비스 포트 허용 규칙 등록 중...
# [SETUP INFO] ✓ Port 8081/tcp registered in ufw firewall.

# 2. 방화벽 규칙 실제 등록 상태 실측 확인
sudo ufw status | grep -E "8081|8089"
```

---

## 2. setup.sh 컴파일 사전 검증 (Pre-Check) 및 3초 이내 완납 실측

```bash
# setup.sh 연속 2회 실행하여 불필요한 8분 compilation이 발생하지 않는지 실측
time ./scripts/setup.sh

# Expected Result:
# 소요 시간 3초 이내
# 출력 로그: "[SETUP INFO] ✓ CUDA GPU 가속 활성화 확인 완료 (기존 바이너리 재사용)"
```

---

## 3. Seed Pack 생성을 통한 exclusion 규칙 및 Wheel 검증

```bash
# 1. 시드 팩 생성 시 config/model_context_profiles.json이 압축에서 제외되는지 실측
uv run ./scripts/make_seed_pack.sh

# 2. 압축파일 내부 확인 (config/model_context_profiles.json이 나오지 않아야 함)
tar -ztvf dist/vllm_serv_seed.tar.gz | grep model_context_profiles.json
# (출력 결과 없어야 함)
```

---

## 4. 웹 대시보드(Port 8089) 재측정 API 및 Dual UI 검증

```bash
# 1. 웹 대시보드 REST API를 통한 캐시 조회
curl -s http://localhost:8089/api/benchmark/profiles | jq .

# 2. 웹 대시보드 REST API를 통한 비동기 재측정 트리거
curl -X POST http://localhost:8089/api/benchmark/rerun -H "Content-Type: application/json" -d '{"full_rebench": false}'
```

---

## 5. 단위 및 통합 테스트 수트 구동 (Strict `uv run`)

```bash
# 방화벽, 쉘 스크립트, 바이너리 검증 pytest 수트 실행
uv run pytest tests/unit/test_firewall_manager.py tests/unit/test_firewall_manager_real.py tests/unit/test_shell_scripts.py -v
```
