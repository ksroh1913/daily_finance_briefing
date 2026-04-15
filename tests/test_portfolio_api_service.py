from app.integrations.kftc.account_info_client import KftcAccountInfoClient
from app.models.transaction import AccountTransaction
from app.services.portfolio_api_service import PortfolioApiService
from app.services.portfolio_snapshot_service import PortfolioSnapshotService
from app.storage.sqlite_repo import PortfolioRepository

from datetime import datetime
from decimal import Decimal


def test_portfolio_api_payloads(tmp_path) -> None:
    repo = PortfolioRepository(db_path=str(tmp_path / "portfolio.db"))

    accounts = KftcAccountInfoClient(sample_path="config/week1_sample_accounts.json").fetch_accounts(use_sample=True)
    repo.replace_accounts(accounts)
    repo.insert_snapshot(PortfolioSnapshotService().build_snapshot(accounts))
    repo.upsert_transactions(
        [
            AccountTransaction(
                tx_id="tx-1",
                institution_name="가상은행A",
                account_num_masked="123",
                tx_type="DEPOSIT",
                amount=Decimal("1000"),
                currency="KRW",
                occurred_at=datetime(2026, 4, 10, 9, 0, 0),
                memo="test",
            )
        ]
    )

    svc = PortfolioApiService(repo)
    dashboard = svc.dashboard()
    accounts_payload = svc.accounts()
    tx_payload = svc.transactions()

    assert dashboard["account_count"] == 2
    assert len(accounts_payload) == 2
    assert len(tx_payload) == 1
