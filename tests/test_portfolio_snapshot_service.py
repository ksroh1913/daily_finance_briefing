from datetime import datetime
from decimal import Decimal

from app.models.account import ExternalAccount
from app.services.portfolio_snapshot_service import PortfolioSnapshotService


def test_snapshot_aggregates_multi_currency_accounts() -> None:
    svc = PortfolioSnapshotService(fx_rates={"KRW": Decimal("1"), "USD": Decimal("1450")})
    accounts = [
        ExternalAccount(
            institution_code="097",
            institution_name="은행A",
            account_num_masked="123",
            account_holder="홍길동",
            account_type="입출금",
            currency="KRW",
            balance=Decimal("1000000"),
            fetched_at=datetime(2026, 4, 10, 10, 0, 0),
        ),
        ExternalAccount(
            institution_code="088",
            institution_name="은행B",
            account_num_masked="987",
            account_holder="홍길동",
            account_type="외화",
            currency="USD",
            balance=Decimal("100"),
            fetched_at=datetime(2026, 4, 10, 10, 0, 0),
        ),
    ]

    snapshot = svc.build_snapshot(accounts, snapshot_at=datetime(2026, 4, 10, 10, 0, 0))
    assert snapshot.total_assets_krw == Decimal("1145000")
    assert snapshot.account_count == 2
