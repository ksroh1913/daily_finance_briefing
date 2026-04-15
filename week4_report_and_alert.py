from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.services.portfolio_report_service import PortfolioReportService
from app.storage.sqlite_repo import PortfolioRepository


def main() -> None:
    now = datetime.now()
    repo = PortfolioRepository(db_path="reports/portfolio.db")
    service = PortfolioReportService(repo)

    monthly = service.monthly_transaction_report(now.year, now.month)
    health = service.health_status()

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    monthly_path = out_dir / f"portfolio-monthly-{now.year}-{now.month:02d}.json"
    health_path = out_dir / "portfolio-health.json"

    monthly_path.write_text(json.dumps(monthly, ensure_ascii=False, indent=2), encoding="utf-8")
    health_path.write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")

    if health["status"] != "ok":
        print(f"[WEEK4:ALERT] health warning: {health}")
    else:
        print(f"[WEEK4] monthly={monthly_path} health={health_path}")


if __name__ == "__main__":
    main()
