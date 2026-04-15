from __future__ import annotations

from typing import Any

from app.storage.sqlite_repo import PortfolioRepository


class PortfolioApiService:
    """Week-3: 대시보드/계좌/거래내역 API payload 생성."""

    def __init__(self, repo: PortfolioRepository) -> None:
        self.repo = repo

    def dashboard(self) -> dict[str, Any]:
        snapshot = self.repo.latest_snapshot()
        accounts = self.repo.list_accounts()

        return {
            "snapshot_at": snapshot.snapshot_at.isoformat(timespec="seconds") if snapshot else None,
            "total_assets_krw": str(snapshot.total_assets_krw) if snapshot else "0",
            "account_count": len(accounts),
        }

    def accounts(self) -> list[dict[str, Any]]:
        return [
            {
                "institution_name": a.institution_name,
                "account_num_masked": a.account_num_masked,
                "account_type": a.account_type,
                "currency": a.currency,
                "balance": str(a.balance),
                "fetched_at": a.fetched_at.isoformat(timespec="seconds"),
            }
            for a in self.repo.list_accounts()
        ]

    def transactions(self, limit: int = 50) -> list[dict[str, Any]]:
        return [
            {
                "tx_id": t.tx_id,
                "institution_name": t.institution_name,
                "account_num_masked": t.account_num_masked,
                "tx_type": t.tx_type,
                "amount": str(t.amount),
                "currency": t.currency,
                "occurred_at": t.occurred_at.isoformat(timespec="seconds"),
                "memo": t.memo,
            }
            for t in self.repo.list_transactions(limit=limit)
        ]
