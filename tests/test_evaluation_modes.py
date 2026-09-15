"""Regressoes de validacao dos modos da CLI de avaliacao."""

from pathlib import Path

import pytest

from scripts import avaliar_modelo


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--calibrate", "--calibration-report", "x"],
        ["--split", "val", "--calibrate"],
        ["--threshold", "0.7", "--calibrate"],
    ],
)
def test_evaluation_rejects_ambiguous_or_legacy_modes(
    tmp_path: Path, args: list[str]
) -> None:
    model = tmp_path / "model.pt"
    model.touch()
    with pytest.raises(SystemExit) as exc_info:
        avaliar_modelo.main(["--model", str(model), *args])
    assert exc_info.value.code == 2
