from app.render.renderer import ReportRenderer
from app.services.market_summary_service import MarketSummaryService


def main() -> None:
    service = MarketSummaryService(config_path="config/tickers.yaml")
    renderer = ReportRenderer(templates_dir="app/render/templates")

    report_data = service.generate()
    html_content = renderer.render_html(report_data)
    renderer.write_outputs(report_data, html_content, output_dir="reports")


if __name__ == "__main__":
    main()
