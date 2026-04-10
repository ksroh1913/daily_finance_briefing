# Daily Finance Briefing

전일 시장 요약 HTML/JSON을 생성하는 배치 프로젝트입니다.

## Step-by-step 구조

1. **수집(Collector)**: `app/collectors/market_collector.py`
   - FinanceDataReader 호출
   - 재시도 및 Close 컬럼 정규화
2. **조립(Service)**: `app/services/market_summary_service.py`
   - `config/tickers.yaml` 로드
   - 섹션별 데이터 구조화 + 표시용 문자열 생성
3. **렌더(Renderer)**: `app/render/renderer.py`
   - Jinja2 템플릿(`app/render/templates/report.html`) 렌더링
4. **저장(Output)**
   - `reports/market-summary-YYYY-MM-DD.html`
   - `reports/market-summary-YYYY-MM-DD.json`
   - `reports/latest.html`, `reports/latest.json`
5. **자동화(GitHub Actions)**
   - `.github/workflows/daily-market-summary.yml`
   - 매일 KST 10:00 실행 + pytest + 리포트 생성 + 변경분 커밋

## Local 실행

```bash
pip install -r requirements.txt
pytest -q
python main.py
# 또는 특정 기준일
python main.py --target-date 2026-04-09
```
