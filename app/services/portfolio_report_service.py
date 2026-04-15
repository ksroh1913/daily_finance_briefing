from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.storage.sqlite_repo import PortfolioRepository


class PortfolioReportService:
    """Week-4: 월간 리포트/헬스체크 생성."""

    def __init__(self, repo: PortfolioRepository) -> None:
        self.repo = repo

    def monthly_transaction_report(self, year: int, month: int) -> dict[str, Any]:
        start = datetime(year, month, 1)
        end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        txs = self.repo.list_transactions_between(start, end)
        inflow = Decimal("0")
        outflow = Decimal("0")
        by_type: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

        for tx in txs:
            by_type[tx.tx_type] += tx.amount
            if tx.tx_type.upper() in {"DEPOSIT", "DIVIDEND", "SELL"}:
                inflow += tx.amount
            else:
                outflow += tx.amount

        return {
            "year": year,
            "month": month,
            "tx_count": len(txs),
            "inflow": str(inflow),
            "outflow": str(outflow),
            "net": str(inflow - outflow),
            "by_type": {k: str(v) for k, v in sorted(by_type.items())},
        }

    def health_status(self) -> dict[str, Any]:
        snapshot = self.repo.latest_snapshot()
        accounts = self.repo.list_accounts()

        return {
            "status": "ok" if snapshot and accounts else "warning",
            "has_snapshot": snapshot is not None,
            "account_count": len(accounts),
            "last_snapshot_at": snapshot.snapshot_at.isoformat(timespec="seconds") if snapshot else None,
        }
