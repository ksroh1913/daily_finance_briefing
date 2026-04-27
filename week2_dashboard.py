from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.services.portfolio_dashboard_service import PortfolioDashboardService
from app.storage.sqlite_repo import PortfolioRepository


def main() -> None:
    repo = PortfolioRepository(db_path="reports/portfolio.db")
    service = PortfolioDashboardService(repo)
    context = service.build_context()

    env = Environment(
        loader=FileSystemLoader("app/render/templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("portfolio_dashboard.html")
    html = template.render(**context)

    out_path = Path("reports/portfolio-dashboard.html")
    out_path.write_text(html, encoding="utf-8")

    print(f"[WEEK2] dashboard generated: {out_path}")


if __name__ == "__main__":
    main()
