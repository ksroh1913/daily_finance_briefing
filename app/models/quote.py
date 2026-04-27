from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(slots=True)
class MarketQuote:
    section: str
    label: str
    symbol: str
    price: Optional[float]
    change: Optional[float]
    change_pct: Optional[float]
    as_of: Optional[date]
    status: str
    error: Optional[str] = None

    @property
    def formatted_price(self) -> str:
        return "N/A" if self.price is None else f"{self.price:,.2f}"

    @property
    def formatted_change(self) -> str:
        if self.change is None:
            return "N/A"
        arrow = "▲" if self.change > 0 else "▼" if self.change < 0 else "-"
        return f"{arrow} {abs(self.change):,.2f}"

    @property
    def formatted_change_pct(self) -> str:
        if self.change_pct is None:
            return "N/A"
        return f"{abs(self.change_pct):.2f}%"
