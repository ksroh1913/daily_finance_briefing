from __future__ import annotations

import argparse
from datetime import date

from app.render.renderer import ReportRenderer
from app.services.market_summary_service import MarketSummaryService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily market summary report")
    parser.add_argument(
        "--target-date",
        type=str,
        default=None,
        help="Target date in YYYY-MM-DD format. Default: today.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_date = date.fromisoformat(args.target_date) if args.target_date else None

    # Step 1) collect + Step 2) normalize/assemble payload
    service = MarketSummaryService(config_path="config/tickers.yaml")
    report_data = service.generate(target_date=target_date)

    # Step 3) render HTML + Step 4) write html/json outputs
    renderer = ReportRenderer(templates_dir="app/render/templates")
    html_content = renderer.render_html(report_data)
    renderer.write_outputs(report_data, html_content, output_dir="reports")


if __name__ == "__main__":
    main()
