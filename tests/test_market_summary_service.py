from datetime import date

from app.models.quote import MarketQuote
from app.services.market_summary_service import MarketSummaryService


class FakeCollector:
    def fetch_quote(self, section: str, label: str, symbol: str, target_date: date) -> MarketQuote:
        return MarketQuote(
            section=section,
            label=label,
            symbol=symbol,
            price=100.0,
            change=1.0,
            change_pct=1.0,
            as_of=target_date,
            status="up",
        )


def test_generate_returns_grouped_sections() -> None:
    service = MarketSummaryService(config_path="config/tickers.yaml", collector=FakeCollector())
    payload = service.generate(target_date=date(2026, 4, 9))

    assert "generated_at" in payload
    assert payload["as_of"] == "2026-04-09"
    assert "국내" in payload["sections"]
    assert payload["sections"]["국내"][0]["display_price"] == "100.00"
    assert payload["sections"]["국내"][0]["display_change"] == "▲ 1.00"
