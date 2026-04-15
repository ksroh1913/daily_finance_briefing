from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.integrations.kftc.account_info_client import KftcAccountInfoClient
from app.models.transaction import AccountTransaction
from app.services.portfolio_snapshot_service import PortfolioSnapshotService
from app.storage.sqlite_repo import PortfolioRepository


def load_sample_transactions(path: str = "config/week3_sample_transactions.json") -> list[AccountTransaction]:
    src = Path(path)
    if not src.exists():
        return []

    payload = json.loads(src.read_text(encoding="utf-8"))
    rows = payload.get("transactions", [])

    return [
        AccountTransaction(
            tx_id=row["tx_id"],
            institution_name=row["institution_name"],
            account_num_masked=row["account_num_masked"],
            tx_type=row["tx_type"],
            amount=Decimal(str(row["amount"])),
            currency=row["currency"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            memo=row.get("memo"),
        )
        for row in rows
    ]


def main() -> None:
    use_sample = os.getenv("KFTC_USE_SAMPLE", "true").lower() == "true"

    client = KftcAccountInfoClient(sample_path="config/week1_sample_accounts.json")
    repo = PortfolioRepository(db_path="reports/portfolio.db")
    snapshot_service = PortfolioSnapshotService()

    accounts = client.fetch_accounts(use_sample=use_sample)
    repo.replace_accounts(accounts)

    snapshot = snapshot_service.build_snapshot(accounts)
    repo.insert_snapshot(snapshot)

    txs = load_sample_transactions()
    if txs:
        repo.upsert_transactions(txs)

    mode = "SAMPLE" if use_sample else "LIVE"
    print(
        f"[WEEK1:{mode}] imported_accounts={len(accounts)} "
        f"total_assets_krw={snapshot.total_assets_krw} imported_txs={len(txs)}"
    )


if __name__ == "__main__":
    main()
