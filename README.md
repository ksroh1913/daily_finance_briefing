# Daily Finance Briefing

전일 시장 요약 HTML/JSON을 매일 생성하기 위한 프로젝트입니다.

## Architecture

- `app/collectors`: 외부 데이터 소스(FinanceDataReader) 수집
- `app/services`: 데이터 정규화 및 리포트 모델 조립
- `app/render`: HTML 템플릿 렌더링 및 출력 저장
- `config/tickers.yaml`: 화면 섹션/심볼 매핑
- `main.py`: 배치 엔트리포인트

## Run locally

```bash
pip install -r requirements.txt
python main.py
```

생성 결과는 `reports/`에 저장됩니다.
