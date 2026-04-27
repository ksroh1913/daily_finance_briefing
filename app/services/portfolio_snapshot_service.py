from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.models.account import AccountSnapshot, ExternalAccount


class PortfolioSnapshotService:
    """Week-1 집계 서비스: 계좌 목록 -> 총자산 스냅샷."""

    def __init__(self, fx_rates: dict[str, Decimal] | None = None) -> None:
        self.fx_rates = fx_rates or {
            "KRW": Decimal("1"),
            "USD": Decimal("1450"),
            "JPY": Decimal("9.8"),
            "EUR": Decimal("1570"),
        }

    def build_snapshot(self, accounts: list[ExternalAccount], snapshot_at: datetime | None = None) -> AccountSnapshot:
        when = snapshot_at or datetime.now()
        total_krw = Decimal("0")

        for account in accounts:
            fx = self.fx_rates.get(account.currency)
            if fx is None:
                raise ValueError(f"Unsupported currency: {account.currency}")
            total_krw += account.balance * fx

        return AccountSnapshot(
            snapshot_at=when,
            total_assets_krw=total_krw,
            account_count=len(accounts),
        )
