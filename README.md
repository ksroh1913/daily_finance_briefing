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
