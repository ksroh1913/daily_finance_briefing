from pathlib import Path

import pytest

from week5_operational_check import verify_artifacts


def test_verify_artifacts_raises_for_missing(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.txt"
    with pytest.raises(RuntimeError):
        verify_artifacts([str(missing_file)])


def test_verify_artifacts_passes_when_exists(tmp_path: Path) -> None:
    ok_file = tmp_path / "ok.txt"
    ok_file.write_text("ok", encoding="utf-8")
    verify_artifacts([str(ok_file)])
