from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from app.storage.sqlite_repo import PortfolioRepository


class PortfolioDashboardService:
    """Week-2: snapshot DB를 화면용 컨텍스트로 변환."""

    def __init__(self, repo: PortfolioRepository) -> None:
        self.repo = repo

    def build_context(self) -> dict[str, Any]:
        snapshot = self.repo.latest_snapshot()
        accounts = self.repo.list_accounts()

        by_institution: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for account in accounts:
            if account.currency == "KRW":
                amount_krw = account.balance
            else:
                # Week-2에서는 단순 표시용 환산. (정밀 환산은 이후 단계에서 FX 테이블 연동)
                amount_krw = Decimal("0")
            by_institution[account.institution_name] += amount_krw

        institution_rows = [
            {
                "institution_name": name,
                "amount_krw": f"{amount:,.0f}",
            }
            for name, amount in sorted(by_institution.items(), key=lambda x: x[1], reverse=True)
        ]

        account_rows = [
            {
                "institution_name": a.institution_name,
                "account_num_masked": a.account_num_masked,
                "account_type": a.account_type,
                "currency": a.currency,
                "balance": f"{a.balance:,.2f}" if a.currency != "KRW" else f"{a.balance:,.0f}",
                "fetched_at": a.fetched_at.isoformat(timespec="seconds"),
            }
            for a in accounts
        ]

        return {
            "snapshot_at": snapshot.snapshot_at.isoformat(timespec="seconds") if snapshot else "N/A",
            "total_assets_krw": f"{snapshot.total_assets_krw:,.0f}" if snapshot else "0",
            "account_count": snapshot.account_count if snapshot else 0,
            "institution_rows": institution_rows,
            "account_rows": account_rows,
        }
