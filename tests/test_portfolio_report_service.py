from datetime import datetime
from decimal import Decimal

from app.models.transaction import AccountTransaction
from app.services.portfolio_report_service import PortfolioReportService
from app.storage.sqlite_repo import PortfolioRepository


def test_monthly_report_and_health(tmp_path) -> None:
    repo = PortfolioRepository(db_path=str(tmp_path / "portfolio.db"))
    repo.upsert_transactions(
        [
            AccountTransaction(
                tx_id="tx-a",
                institution_name="은행A",
                account_num_masked="123",
                tx_type="DEPOSIT",
                amount=Decimal("100"),
                currency="KRW",
                occurred_at=datetime(2026, 4, 1, 9, 0, 0),
                memo=None,
            ),
            AccountTransaction(
                tx_id="tx-b",
                institution_name="은행A",
                account_num_masked="123",
                tx_type="WITHDRAWAL",
                amount=Decimal("40"),
                currency="KRW",
                occurred_at=datetime(2026, 4, 2, 9, 0, 0),
                memo=None,
            ),
        ]
    )

    svc = PortfolioReportService(repo)
    monthly = svc.monthly_transaction_report(2026, 4)
    health = svc.health_status()

    assert monthly["tx_count"] == 2
    assert monthly["net"] == "60"
    assert health["status"] == "warning"
