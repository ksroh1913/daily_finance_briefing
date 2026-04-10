from __future__ import annotations

import time
from datetime import date, timedelta

import FinanceDataReader as fdr
import pandas as pd

from app.models.quote import MarketQuote


class MarketCollector:
    """Step 1: FinanceDataReader에서 종가 데이터 수집."""

    LOOKBACK_DAYS = 10
    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 1.0

    def fetch_quote(self, section: str, label: str, symbol: str, target_date: date) -> MarketQuote:
        start_date = target_date - timedelta(days=self.LOOKBACK_DAYS)

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                frame = fdr.DataReader(symbol, start_date.isoformat(), target_date.isoformat())
                return self._build_quote(section, label, symbol, frame)
            except Exception as exc:
                if attempt >= self.MAX_RETRIES:
                    return MarketQuote(
                        section=section,
                        label=label,
                        symbol=symbol,
                        price=None,
                        change=None,
                        change_pct=None,
                        as_of=None,
                        status="error",
                        error=self._short_error(str(exc)),
                    )
                time.sleep(self.RETRY_DELAY_SECONDS)

        return MarketQuote(
            section=section,
            label=label,
            symbol=symbol,
            price=None,
            change=None,
            change_pct=None,
            as_of=None,
            status="error",
            error="Unknown collection failure",
        )

    def fetch_quote_with_fallback(
        self,
        section: str,
        label: str,
        symbols: list[str],
        target_date: date,
    ) -> MarketQuote:
        """Try multiple symbols in order and return the first successful quote."""
        errors: list[str] = []

        for symbol in symbols:
            quote = self.fetch_quote(section=section, label=label, symbol=symbol, target_date=target_date)
            if quote.status in {"up", "down", "flat"}:
                return quote
            if quote.error:
                errors.append(f"{symbol}: {quote.error}")

        merged_error = " | ".join(errors) if errors else "All symbol fallbacks failed"
        return MarketQuote(
            section=section,
            label=label,
            symbol=",".join(symbols),
            price=None,
            change=None,
            change_pct=None,
            as_of=None,
            status="error",
            error=self._short_error(merged_error),
        )

    def _build_quote(self, section: str, label: str, symbol: str, frame: pd.DataFrame) -> MarketQuote:
        if frame.empty:
            return MarketQuote(
                section=section,
                label=label,
                symbol=symbol,
                price=None,
                change=None,
                change_pct=None,
                as_of=None,
                status="missing",
                error="No rows returned from FinanceDataReader",
            )

        normalized = self._normalize_frame(frame)
        if "Close" not in normalized.columns:
            return MarketQuote(
                section=section,
                label=label,
                symbol=symbol,
                price=None,
                change=None,
                change_pct=None,
                as_of=None,
                status="missing",
                error="Close column not found",
            )

        closes = normalized["Close"].dropna()
        if len(closes) < 2:
            return MarketQuote(
                section=section,
                label=label,
                symbol=symbol,
                price=None,
                change=None,
                change_pct=None,
                as_of=None,
                status="missing",
                error="Insufficient close prices to compute delta",
            )

        latest_close = float(closes.iloc[-1])
        prev_close = float(closes.iloc[-2])
        change = latest_close - prev_close
        change_pct = (change / prev_close * 100.0) if prev_close else 0.0
        as_of = closes.index[-1].date()
        status = "up" if change > 0 else "down" if change < 0 else "flat"

        return MarketQuote(
            section=section,
            label=label,
            symbol=symbol,
            price=latest_close,
            change=change,
            change_pct=change_pct,
            as_of=as_of,
            status=status,
        )

    @staticmethod
    def _short_error(message: str, max_len: int = 180) -> str:
        if len(message) <= max_len:
            return message
        return f"{message[:max_len-3]}..."

    @staticmethod
    def _normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
        if "Close" in frame.columns:
            return frame

        lower_cols = {col.lower(): col for col in frame.columns}
        if "close" in lower_cols:
            return frame.rename(columns={lower_cols["close"]: "Close"})

        return frame
