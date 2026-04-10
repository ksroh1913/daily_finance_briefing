from __future__ import annotations

from datetime import date, timedelta

import FinanceDataReader as fdr
import pandas as pd

from app.models.quote import MarketQuote


class MarketCollector:
    """Collects market series data and computes previous-day change metrics."""

    LOOKBACK_DAYS = 10

    def fetch_quote(self, section: str, label: str, symbol: str, target_date: date) -> MarketQuote:
        start_date = target_date - timedelta(days=self.LOOKBACK_DAYS)

        try:
            frame = fdr.DataReader(symbol, start_date.isoformat(), target_date.isoformat())
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
        except Exception as exc:
            return MarketQuote(
                section=section,
                label=label,
                symbol=symbol,
                price=None,
                change=None,
                change_pct=None,
                as_of=None,
                status="error",
                error=str(exc),
            )

    @staticmethod
    def _normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
        if "Close" in frame.columns:
            return frame
        lower_cols = {col.lower(): col for col in frame.columns}
        if "close" in lower_cols:
            return frame.rename(columns={lower_cols["close"]: "Close"})
        return frame
