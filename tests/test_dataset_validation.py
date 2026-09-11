from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

from model_lifecycle.dataset_validation import validate_dataset
from model_lifecycle.inspection_classes import CLASS_NAMES


def build_dataset(root: Path) -> None:
    for split_index, split in enumerate(("train", "val", "test")):
        for class_index, class_name in enumerate(CLASS_NAMES):
            directory = root / split / class_name
            directory.mkdir(parents=True)
            Image.new(
                "RGB",
                (8, 8),
                color=(split_index * 50, class_index * 40, 10),
            ).save(directory / f"{split}-{class_name}.png")


def test_valid_dataset(tmp_path: Path) -> None:
    build_dataset(tmp_path)
    report = validate_dataset(tmp_path)
    assert report.valid
    assert report.total_images == 12
    assert report.warnings


def test_missing_class_is_invalid(tmp_path: Path) -> None:
    build_dataset(tmp_path)
    shutil.rmtree(tmp_path / "test" / "04_amassado")
    report = validate_dataset(tmp_path)
    assert not report.valid
    assert any("Classes ausentes em test" in error for error in report.errors)


def test_duplicate_across_splits_is_invalid(tmp_path: Path) -> None:
    build_dataset(tmp_path)
    source = tmp_path / "train" / "01_conforme" / "train-01_conforme.png"
    target = tmp_path / "test" / "01_conforme" / "duplicada.png"
    shutil.copy2(source, target)
    report = validate_dataset(tmp_path)
    assert not report.valid
    assert report.duplicate_hashes
