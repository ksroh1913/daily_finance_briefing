from __future__ import annotations

from app.integrations.kftc.account_info_client import KftcAccountInfoClient
from app.services.portfolio_snapshot_service import PortfolioSnapshotService
from app.storage.sqlite_repo import PortfolioRepository


def main() -> None:
    client = KftcAccountInfoClient(sample_path="config/week1_sample_accounts.json")
    repo = PortfolioRepository(db_path="reports/portfolio.db")
    snapshot_service = PortfolioSnapshotService()

    accounts = client.fetch_accounts()
    repo.replace_accounts(accounts)

    snapshot = snapshot_service.build_snapshot(accounts)
    repo.insert_snapshot(snapshot)

    print(f"[WEEK1] imported_accounts={len(accounts)} total_assets_krw={snapshot.total_assets_krw}")


if __name__ == "__main__":
    main()
