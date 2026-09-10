"""Adaptador de runtime e execução de inferência."""

from __future__ import annotations

from typing import Any, Protocol

from model_lifecycle.inspection_classes import canonical_class

from .schemas import Classification


class Classifier(Protocol):
    """Contrato estrutural dos classificadores injetados em ``InferenceEngine``.

    Uma implementação não precisa herdar deste **protocolo**; basta fornecer o método
    ``predict`` com a assinatura definida abaixo. Isso permite substituir o runtime
    real por classificadores controlados durante os **testes**.
    """

    def predict(self, image: Any) -> Classification: ...


class UltralyticsClassifier:
    """Carrega checkpoints PyTorch ou TFLite pela interface uniforme do YOLO."""

    def __init__(self, model_path: str, image_size: int) -> None:
        try:
            from ultralytics import YOLO
        except ModuleNotFoundError as exc:
            raise RuntimeError("Ultralytics nao esta instalado") from exc
        self.model = YOLO(model_path, task="classify")
        self.image_size = image_size

    def predict(self, image: Any) -> Classification:
        results = self.model.predict(source=image, imgsz=self.image_size, verbose=False)
        if not results or results[0].probs is None:
            raise RuntimeError("O runtime nao retornou probabilidades de classificacao")
        result = results[0]
        class_id = int(result.probs.top1)
        confidence = float(result.probs.top1conf)
        return Classification(
            class_name=canonical_class(str(result.names[class_id])),
            confidence=confidence,
        )
