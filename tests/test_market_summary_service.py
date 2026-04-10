import json
from datetime import date
from pathlib import Path

from app.models.quote import MarketQuote
from app.services.market_summary_service import MarketSummaryService


class FakeCollector:
    def fetch_quote_with_fallback(self, section: str, label: str, symbols: list[str], target_date: date) -> MarketQuote:
        return MarketQuote(
            section=section,
            label=label,
            symbol=symbols[0],
            price=100.0,
            change=1.0,
            change_pct=1.0,
            as_of=target_date,
            status="up",
        )


class ErrorCollector:
    def fetch_quote_with_fallback(self, section: str, label: str, symbols: list[str], target_date: date) -> MarketQuote:
        return MarketQuote(
            section=section,
            label=label,
            symbol=symbols[0],
            price=None,
            change=None,
            change_pct=None,
            as_of=None,
            status="error",
            error="source failed",
        )


def test_generate_returns_grouped_sections() -> None:
    service = MarketSummaryService(config_path="config/tickers.yaml", collector=FakeCollector())
    payload = service.generate(target_date=date(2026, 4, 9))

    assert "generated_at" in payload
    assert payload["as_of"] == "2026-04-09"
    assert "국내" in payload["sections"]
    assert payload["sections"]["국내"][0]["display_price"] == "100.00"
    assert payload["sections"]["국내"][0]["display_change"] == "▲ 1.00"


def test_normalize_symbols_supports_list_or_single() -> None:
    assert MarketSummaryService._normalize_symbols({"label": "금", "symbol": "GC=F"}) == ["GC=F"]
    assert MarketSummaryService._normalize_symbols({"label": "금", "symbols": ["GC=F", "XAU/USD"]}) == [
        "GC=F",
        "XAU/USD",
    ]


def test_cache_fallback_used_when_source_fails(tmp_path: Path) -> None:
    cache_path = tmp_path / "latest.json"
    cache_payload = {
        "sections": {
            "상품": [
                {
                    "label": "금",
                    "price": 3000.0,
                    "change": 10.0,
                    "change_pct": 0.3,
                    "as_of": "2026-04-08",
                }
            ]
        }
    }
    cache_path.write_text(json.dumps(cache_payload), encoding="utf-8")

    service = MarketSummaryService(
        config_path="config/tickers.yaml",
        collector=ErrorCollector(),
        cache_path=str(cache_path),
    )
    payload = service.generate(target_date=date(2026, 4, 9))

    commodity_rows = payload["sections"]["상품"]
    gold = next(row for row in commodity_rows if row["label"] == "금")
    assert gold["price"] == 3000.0
    assert "cached previous value" in gold["error"]
