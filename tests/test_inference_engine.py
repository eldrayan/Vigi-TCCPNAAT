from __future__ import annotations

import pytest

from edge.inference.engine import InferenceEngine, decide
from edge.inference.schemas import Classification
from model_lifecycle.inspection_classes import CLASS_NAMES
from model_lifecycle.manifest import ModelManifest


def manifest() -> ModelManifest:
    return ModelManifest(
        model_path="model.pt",
        format="pytorch",
        classes=CLASS_NAMES,
        confidence_threshold=0.70,
        image_size=224,
        dataset_hash="abc",
        ultralytics_version="8.2.0",
        metrics={
            "accuracy": 0.95,
            "false_negative_rate": 0.05,
            "false_positive_rate": 0.05,
        },
    )


class StubClassifier:
    def __init__(self, result: Classification | None = None, fail: bool = False):
        self.result = result
        self.fail = fail

    def predict(self, _image):
        if self.fail:
            raise RuntimeError("runtime indisponivel")
        return self.result


def test_conforming_decision() -> None:
    result = decide(Classification("01_conforme", 0.95), 0.70, 12.0, "pytorch")
    assert result.result == "CONFORME"
    assert result.category is None
    assert result.nonconformity_type is None
    assert result.technical_failure_type is None


def test_defect_decision() -> None:
    result = decide(Classification("02_sem_tampa", 0.95), 0.70, 12.0, "pytorch")
    assert result.result == "NAO_CONFORME"
    assert result.category == "ANOMALIA_PRODUTO"
    assert result.nonconformity_type == "SEM_TAMPA"
    assert result.technical_failure_type is None


def test_low_confidence_is_technical_failure() -> None:
    result = decide(Classification("01_conforme", 0.40), 0.70, 12.0, "pytorch")
    assert result.category == "FALHA_TECNICA"
    assert result.nonconformity_type is None
    assert result.technical_failure_type == "BAIXA_CONFIANCA"


def test_runtime_error_is_fail_safe() -> None:
    engine = InferenceEngine(manifest(), StubClassifier(fail=True))
    result = engine.inspect(object())
    assert result.result == "NAO_CONFORME"
    assert result.technical_failure_type == "ERRO_INFERENCIA"


def test_engine_always_uses_manifest_threshold() -> None:
    engine = InferenceEngine(
        manifest(), StubClassifier(Classification("01_conforme", 0.69))
    )
    assert engine.inspect(object()).technical_failure_type == "BAIXA_CONFIANCA"


def test_inference_cli_rejects_threshold_override() -> None:
    from scripts import inferir

    with pytest.raises(SystemExit) as exc_info:
        inferir.main(
            [
                "--manifest",
                "models/active/manifest.json",
                "--image",
                "image.jpg",
                "--threshold",
                "0.5",
            ]
        )
    assert exc_info.value.code == 2
