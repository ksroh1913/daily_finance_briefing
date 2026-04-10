from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from app.collectors.market_collector import MarketCollector
from app.models.quote import MarketQuote


class MarketSummaryService:
    """Step 2~3: 설정 로드 + 시장 데이터 조립 서비스."""

    def __init__(
        self,
        config_path: str = "config/tickers.yaml",
        collector: MarketCollector | None = None,
        cache_path: str = "reports/latest.json",
    ) -> None:
        self.config_path = Path(config_path)
        self.collector = collector or MarketCollector()
        self.cache_path = Path(cache_path)

    def generate(self, target_date: date | None = None) -> dict[str, Any]:
        """Generate report payload for a target date (default: today)."""
        config = self._load_config()
        now = datetime.now()
        기준일 = target_date or now.date()
        cached_map = self._load_cache_map()

        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        as_of_dates = []

        for section in config["sections"]:
            section_name = section["name"]
            for item in section["items"]:
                symbols = self._normalize_symbols(item)
                quote = self.collector.fetch_quote_with_fallback(
                    section=section_name,
                    label=item["label"],
                    symbols=symbols,
                    target_date=기준일,
                )
                quote = self._apply_cache_if_needed(quote, cached_map)

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
    def _normalize_symbols(item: dict[str, Any]) -> list[str]:
        if "symbols" in item:
            symbols = item["symbols"]
            if not isinstance(symbols, list) or not symbols:
                raise ValueError(f"Invalid symbols list for item: {item}")
            return [str(s) for s in symbols]

        if "symbol" not in item:
            raise ValueError(f"Item must contain 'symbol' or 'symbols': {item}")

        return [str(item["symbol"])]

    def _apply_cache_if_needed(self, quote: MarketQuote, cached_map: dict[tuple[str, str], dict[str, Any]]) -> MarketQuote:
        if quote.status in {"up", "down", "flat"}:
            return quote

        cached = cached_map.get((quote.section, quote.label))
        if not cached:
            return quote

        price = cached.get("price")
        if price is None:
            return quote

        as_of_raw = cached.get("as_of")
        as_of = date.fromisoformat(as_of_raw) if as_of_raw else None

        return MarketQuote(
            section=quote.section,
            label=quote.label,
            symbol=quote.symbol,
            price=float(price),
            change=cached.get("change"),
            change_pct=cached.get("change_pct"),
            as_of=as_of,
            status="flat",
            error=(quote.error or "data source error") + " | cached previous value",
        )

    def _load_cache_map(self) -> dict[tuple[str, str], dict[str, Any]]:
        if not self.cache_path.exists():
            return {}

        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

        sections = payload.get("sections", {})
        cache_map: dict[tuple[str, str], dict[str, Any]] = {}
        if not isinstance(sections, dict):
            return cache_map

        for section_name, rows in sections.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                label = row.get("label")
                if label:
                    cache_map[(section_name, label)] = row
        return cache_map

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
            "display_price": quote.formatted_price,
            "display_change": quote.formatted_change,
            "display_change_pct": quote.formatted_change_pct,
        }

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as fp:
            config = yaml.safe_load(fp)

        if not isinstance(config, dict) or "sections" not in config:
            raise ValueError("Invalid config: expected top-level 'sections'")

        return config
