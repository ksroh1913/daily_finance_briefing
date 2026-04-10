from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ReportRenderer:
    def __init__(self, templates_dir: str = "app/render/templates") -> None:
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_html(self, context: dict[str, Any]) -> str:
        template = self.env.get_template("report.html")
        return template.render(**context)

    @staticmethod
    def write_outputs(report_data: dict[str, Any], html_content: str, output_dir: str = "reports") -> None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        date_token = report_data["generated_at"].split("T", maxsplit=1)[0]
        html_path = out / f"market-summary-{date_token}.html"
        json_path = out / f"market-summary-{date_token}.json"
        latest_html = out / "latest.html"
        latest_json = out / "latest.json"

        html_path.write_text(html_content, encoding="utf-8")
        json_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
        latest_html.write_text(html_content, encoding="utf-8")
        latest_json.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
