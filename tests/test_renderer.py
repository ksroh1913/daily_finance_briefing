from app.render.renderer import ReportRenderer


def test_renderer_creates_html() -> None:
    renderer = ReportRenderer(templates_dir="app/render/templates")
    html = renderer.render_html(
        {
            "generated_at": "2026-04-10T10:00:00",
            "as_of": "2026-04-09",
            "sections": {
                "국내": [
                    {
                        "label": "코스피",
                        "display_price": "1,000.00",
                        "display_change": "▲ 10.00",
                        "display_change_pct": "1.00%",
                        "change": 10.0,
                        "change_pct": 1.0,
                        "status": "up",
                        "error": None,
                    }
                ]
            },
        }
    )

    assert "전일 시장 요약" in html
    assert "코스피" in html
    assert "▲ 10.00 (1.00%)" in html
