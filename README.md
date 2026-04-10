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
  - 추후 금융결제원 API로 교체 가능한 어댑터 인터페이스
  - 현재는 `config/week1_sample_accounts.json` 샘플을 공통 모델로 정규화
- `app/storage/sqlite_repo.py`
  - `accounts`, `snapshots` 테이블 생성 및 저장
- `app/services/portfolio_snapshot_service.py`
  - 다중 통화 계좌를 KRW로 환산해 총자산 스냅샷 집계
- `week1_bootstrap.py`
  - 샘플 계좌 수집 -> DB 저장 -> 스냅샷 저장까지 한번에 실행

실행:

```bash
python week1_bootstrap.py
```

결과:
- `reports/portfolio.db` 생성
- 최신 스냅샷 저장
