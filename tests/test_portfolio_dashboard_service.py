from app.services.portfolio_dashboard_service import PortfolioDashboardService
from app.storage.sqlite_repo import PortfolioRepository
from app.integrations.kftc.account_info_client import KftcAccountInfoClient
from app.services.portfolio_snapshot_service import PortfolioSnapshotService


def test_dashboard_context_contains_kpis(tmp_path) -> None:
    db_path = tmp_path / "portfolio.db"
    repo = PortfolioRepository(db_path=str(db_path))

    client = KftcAccountInfoClient(sample_path="config/week1_sample_accounts.json")
    accounts = client.fetch_accounts(use_sample=True)
    repo.replace_accounts(accounts)

    snapshot = PortfolioSnapshotService().build_snapshot(accounts)
    repo.insert_snapshot(snapshot)

    context = PortfolioDashboardService(repo).build_context()

    assert context["account_count"] == 2
    assert context["total_assets_krw"] != "0"
    assert len(context["account_rows"]) == 2
