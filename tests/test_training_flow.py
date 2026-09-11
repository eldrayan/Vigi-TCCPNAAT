"""Regressoes do fluxo de treinamento sem augmentation adicional."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image, ImageDraw

from scripts import treinar_modelo


class FakeTrainerBase:
    def __init__(self) -> None:
        self.args = object()


class FakeDataset:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


def test_custom_trainer_disables_augmentation_for_every_split() -> None:
    trainer_type = treinar_modelo.create_no_augmentation_trainer(
        FakeTrainerBase, FakeDataset
    )
    trainer = trainer_type()

    for split in ("train", "val", "test"):
        dataset = trainer.build_dataset("dataset", split)
        assert dataset.kwargs == {
            "root": "dataset",
            "args": trainer.args,
            "augment": False,
            "prefix": split,
        }


def test_training_uses_trainer_paths_and_writes_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    best = tmp_path / "checkpoint-em-local-nao-convencional.pt"
    best.write_bytes(b"weights")
    config = tmp_path / "training.yaml"
    config.write_text(
        "model: yolov8n-cls.pt\nname: baseline\nimgsz: 224\naugment: false\n",
        encoding="utf-8",
    )

    class FakeYOLO:
        def __init__(self, model_name: str) -> None:
            assert model_name == "yolov8n-cls.pt"
            self.trainer = None

        def train(self, **kwargs: object) -> object:
            assert kwargs["trainer"].__name__ == "NoAugmentationClassificationTrainer"
            self.trainer = type(
                "TrainerState", (), {"best": best, "save_dir": run_dir}
            )()
            return object()  # O retorno nao possui save_dir deliberadamente.

    monkeypatch.setattr(treinar_modelo, "dataset_hash", lambda _: "dataset-sha")
    output = tmp_path / "candidates"
    summary = treinar_modelo.train_model(
        tmp_path / "dataset",
        config,
        output,
        FakeYOLO,
        FakeTrainerBase,
        FakeDataset,
        "8.4.146",
    )

    candidate = output / "vigi-yolov8n-cls-baseline.pt"
    assert candidate.read_bytes() == b"weights"
    assert summary["checkpoint"] == str(candidate)
    assert summary["run_directory"] == str(run_dir)
    assert "tflite" not in summary
    persisted = json.loads(
        (run_dir / "vigi-training-summary.json").read_text(encoding="utf-8")
    )
    assert persisted == summary


def test_training_rejects_missing_checkpoint_without_creating_output(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    config = tmp_path / "training.yaml"
    config.write_text(
        "model: yolov8n-cls.pt\nname: baseline\naugment: false\n",
        encoding="utf-8",
    )

    class FakeYOLO:
        def __init__(self, _: str) -> None:
            self.trainer = None

        def train(self, **_: object) -> None:
            self.trainer = type(
                "TrainerState",
                (),
                {"best": tmp_path / "missing.pt", "save_dir": run_dir},
            )()

    output = tmp_path / "candidates"
    with pytest.raises(FileNotFoundError, match="Checkpoint nao gerado"):
        treinar_modelo.train_model(
            tmp_path / "dataset",
            config,
            output,
            FakeYOLO,
            FakeTrainerBase,
            FakeDataset,
            "8.4.146",
        )
    assert not output.exists()


def test_training_rejects_missing_trainer(tmp_path: Path) -> None:
    config = tmp_path / "training.yaml"
    config.write_text(
        "model: yolov8n-cls.pt\nname: baseline\naugment: false\n",
        encoding="utf-8",
    )

    class FakeYOLO:
        def __init__(self, _: str) -> None:
            self.trainer = None

        def train(self, **_: object) -> None:
            return None

    with pytest.raises(RuntimeError, match="Trainer indisponivel"):
        treinar_modelo.train_model(
            tmp_path / "dataset",
            config,
            tmp_path / "candidates",
            FakeYOLO,
            FakeTrainerBase,
            FakeDataset,
            "8.4.146",
        )


def test_training_cli_no_longer_accepts_tflite_export() -> None:
    with pytest.raises(SystemExit) as exc_info:
        treinar_modelo.main(["--export-tflite"])
    assert exc_info.value.code == 2


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
