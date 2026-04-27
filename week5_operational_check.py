from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def verify_artifacts(paths: list[str]) -> None:
    missing = [p for p in paths if not Path(p).exists()]
    if missing:
        raise RuntimeError(f"Missing artifacts: {missing}")


def main() -> None:
    run(["python", "week1_bootstrap.py"])
    run(["python", "week2_dashboard.py"])
    run(["python", "week4_report_and_alert.py"])

    verify_artifacts(
        [
            "reports/portfolio.db",
            "reports/portfolio-dashboard.html",
            "reports/portfolio-health.json",
        ]
    )

    print("[WEEK5] operational check passed")


if __name__ == "__main__":
    main()
