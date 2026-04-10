from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from app.collectors.market_collector import MarketCollector
from app.models.quote import MarketQuote


class MarketSummaryService:
    def __init__(self, config_path: str = "config/tickers.yaml") -> None:
        self.config_path = Path(config_path)
        self.collector = MarketCollector()

    def generate(self) -> dict[str, Any]:
        config = self._load_config()
        now = datetime.now()

        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        as_of_dates = []

        for section in config["sections"]:
            section_name = section["name"]
            for item in section["items"]:
                quote = self.collector.fetch_quote(
                    section=section_name,
                    label=item["label"],
                    symbol=item["symbol"],
                    target_date=now.date(),
                )
                grouped[section_name].append(self._serialize_quote(quote))
                if quote.as_of:
                    as_of_dates.append(quote.as_of)

        report_as_of = max(as_of_dates).isoformat() if as_of_dates else None
        return {
            "generated_at": now.isoformat(timespec="seconds"),
            "as_of": report_as_of,
            "sections": dict(grouped),
        }

    @staticmethod
    def _serialize_quote(quote: MarketQuote) -> dict[str, Any]:
        return {
            "section": quote.section,
            "label": quote.label,
            "symbol": quote.symbol,
            "price": quote.price,
            "change": quote.change,
            "change_pct": quote.change_pct,
            "as_of": quote.as_of.isoformat() if quote.as_of else None,
            "status": quote.status,
            "error": quote.error,
        }

    def _load_config(self) -> dict[str, Any]:
        with self.config_path.open("r", encoding="utf-8") as fp:
            return yaml.safe_load(fp)
