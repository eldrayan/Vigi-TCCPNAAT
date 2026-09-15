"""Regressoes do dataset de treinamento sem augmentations aleatorias."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image, ImageDraw

from scripts import treinar_modelo


def test_real_ultralytics_no_augmentation_transform_is_deterministic(
    tmp_path: Path,
) -> None:
    pytest.importorskip("ultralytics")
    from ultralytics.data.dataset import ClassificationDataset

    args = SimpleNamespace(
        fraction=1.0,
        cache=False,
        single_cls=False,
        scale=0.5,
        imgsz=32,
        fliplr=0.5,
        flipud=0.5,
        erasing=0.4,
        auto_augment="randaugment",
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
    )

    class TrainerBase:
        def __init__(self) -> None:
            self.args = args

    trainer_type = treinar_modelo.create_no_augmentation_trainer(
        TrainerBase, ClassificationDataset
    )
    image_dir = tmp_path / "train" / "01_conforme"
    image_dir.mkdir(parents=True)
    image = Image.new("RGB", (48, 32), "black")
    ImageDraw.Draw(image).rectangle((0, 0, 23, 31), fill="red")
    image.save(image_dir / "sample.png")

    dataset = trainer_type().build_dataset(str(tmp_path / "train"), "train")
    first = dataset[0]["img"]
    second = dataset[0]["img"]
    assert first.equal(second)
