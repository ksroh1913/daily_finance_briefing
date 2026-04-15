# Daily Finance Briefing

전일 시장 요약 HTML/JSON을 생성하는 배치 프로젝트입니다.

## Step-by-step 구조

1. **수집(Collector)**: `app/collectors/market_collector.py`
   - FinanceDataReader 호출
   - 재시도 및 Close 컬럼 정규화
   - `symbols` fallback 순차 시도 (예: 금/은)
2. **조립(Service)**: `app/services/market_summary_service.py`
   - `config/tickers.yaml` 로드
   - 섹션별 데이터 구조화 + 표시용 문자열 생성
   - `symbol` 또는 `symbols` 둘 다 지원
   - 실시간 조회 실패 시 `reports/latest.json` 캐시값으로 대체
3. **렌더(Renderer)**: `app/render/renderer.py`
   - Jinja2 템플릿(`app/render/templates/report.html`) 렌더링
4. **저장(Output)**
   - `reports/market-summary-YYYY-MM-DD.html`
   - `reports/market-summary-YYYY-MM-DD.json`
   - `reports/latest.html`, `reports/latest.json`
5. **자동화(GitHub Actions)**
   - `.github/workflows/daily-market-summary.yml`
   - 매일 KST 10:00 실행 + pytest + 리포트 생성 + 변경분 커밋

## 금/은 오류 대응

Yahoo 원자재 심볼(`XAU/USD`, `XAG/USD`)이 간헐적으로 실패할 수 있어,
`config/tickers.yaml`에서 `symbols` fallback을 사용합니다.

- 금: `GC=F` -> 실패 시 `XAU/USD`
- 은: `SI=F` -> 실패 시 `XAG/USD`

추가로, fallback도 실패하면 이전 실행에서 성공한 `latest.json` 값을 사용해
N/A를 줄이도록 처리했습니다(오류 라벨에 cached 표시).

## Local 실행

```bash
pip install -r requirements.txt
pytest -q

# 보고서 생성만
python main.py

# 특정 기준일로 생성
python main.py --target-date 2026-04-09

# 생성 후 바로 보기(로컬 서버)
python main.py --serve
# 또는 포트 지정
python main.py --serve --port 8080
```

서버 실행 후 브라우저에서 아래 URL을 열면 됩니다.

- `http://localhost:8000/reports/latest.html`

## 4주 로드맵 - 1주차 구현 상태

1주차 목표(스키마/수집 정규화/스냅샷) 반영:

- `app/integrations/kftc/account_info_client.py`
  - 금융결제원 계좌통합조회 API(`accountinfo/list`)용 어댑터
  - 샘플 모드/라이브 모드 둘 다 지원
- `app/storage/sqlite_repo.py`
  - `accounts`, `snapshots` 테이블 생성 및 저장
- `app/services/portfolio_snapshot_service.py`
  - 다중 통화 계좌를 KRW로 환산해 총자산 스냅샷 집계
- `week1_bootstrap.py`
  - 계좌 수집 -> DB 저장 -> 스냅샷 저장까지 한번에 실행

실행:

```bash
# 샘플 모드(기본)
python week1_bootstrap.py

# 라이브 모드(금융결제원 API)
export KFTC_USE_SAMPLE=false
export KFTC_ACCESS_TOKEN="<token>"
export KFTC_USER_SEQ_NO="<user_seq_no>"
export KFTC_AUTH_CODE="<auth_code>"
python week1_bootstrap.py

# 라이브 모드에서 계좌별 잔액(balance/fin_num)까지 조회하려면
export KFTC_INCLUDE_BALANCE=true
python week1_bootstrap.py
```

결과:
- `reports/portfolio.db` 생성
- 최신 스냅샷 저장

## 4주 로드맵 - 2주차 구현 상태

2주차 목표(대시보드 KPI/기관별 요약/계좌목록) 반영:

- `app/services/portfolio_dashboard_service.py`
  - `portfolio.db`에서 최신 스냅샷 + 계좌목록을 읽어 화면 컨텍스트 생성
- `app/render/templates/portfolio_dashboard.html`
  - KPI 카드(총자산/계좌수/기관수)
  - 기관별 금액 표
  - 계좌 목록 표
- `week2_dashboard.py`
  - 대시보드 HTML(`reports/portfolio-dashboard.html`) 생성

실행:

```bash
# 1) 1주차 스냅샷 생성
python week1_bootstrap.py

# 2) 2주차 대시보드 렌더링
python week2_dashboard.py

# 3) 브라우저 확인
python -m http.server 8000
# http://localhost:8000/reports/portfolio-dashboard.html
```

## 4주 로드맵 - 3주차 구현 상태

3주차 목표(API 레이어: dashboard/accounts/transactions) 반영:

- `app/models/transaction.py`
  - 거래내역 도메인 모델 추가
- `app/storage/sqlite_repo.py`
  - `transactions` 테이블 추가
  - 거래 upsert/list 기능 추가
- `app/services/portfolio_api_service.py`
  - `/api/dashboard`, `/api/accounts`, `/api/transactions`용 payload 생성
- `week3_api_server.py`
  - 표준 라이브러리 HTTP 서버 기반 JSON API 제공

실행:

```bash
# 1) 데이터 적재 (계좌 + 거래내역)
python week1_bootstrap.py

# 2) API 서버 실행
python week3_api_server.py

# 3) 확인
# http://localhost:8100/api/dashboard
# http://localhost:8100/api/accounts
# http://localhost:8100/api/transactions?limit=20

# (선택) API 키 보호
# export PORTFOLIO_API_KEY="your-secret"
# curl -H "X-API-Key: your-secret" http://localhost:8100/api/dashboard
```

## 4주 로드맵 - 4주차 구현 상태

4주차 목표(리포트 아카이브 + 알림/모니터링) 반영:

- `app/services/portfolio_report_service.py`
  - 월간 거래 리포트(inflow/outflow/net/by_type) 생성
  - 시스템 헬스 상태(has_snapshot/account_count/last_snapshot_at) 생성
- `week4_report_and_alert.py`
  - 월간 리포트 JSON + 헬스 JSON 파일 생성
  - 헬스 warning 시 콘솔 알림 출력
- `app/storage/sqlite_repo.py`
  - 기간별 거래 조회 `list_transactions_between()` 추가

실행:

```bash
# 1) 기초 데이터 적재
python week1_bootstrap.py

# 2) 4주차 리포트/헬스 생성
python week4_report_and_alert.py

# (선택) 헬스 warning 시 웹훅 알림
# export ALERT_WEBHOOK_URL="https://your.webhook/url"
# python week4_report_and_alert.py

# 3) 결과 확인
# reports/portfolio-monthly-YYYY-MM.json
# reports/portfolio-health.json
```

## 4주 로드맵 이후 - 운영 자동화(Week-5)

운영 안정화를 위해 portfolio 파이프라인 자동 점검 단계를 추가:

- `week5_operational_check.py`
  - `week1_bootstrap.py` → `week2_dashboard.py` → `week4_report_and_alert.py` 순서 실행
  - 핵심 결과물 존재 여부 검증
- `.github/workflows/portfolio-ops.yml`
  - 매일 KST 10:30 실행
  - 테스트 + 운영 점검 실행
  - `reports/` 변경 시 자동 커밋

실행:

```bash
python week5_operational_check.py
```
