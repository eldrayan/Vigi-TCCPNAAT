"""Orquestracao da inferencia."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from model_lifecycle.inspection_classes import CLASS_CODES, canonical_class
from model_lifecycle.manifest import ModelManifest

from .adapters import Classifier, UltralyticsClassifier
from .schemas import Classification, InspectionDecision


def decide(
    classification: Classification,
    threshold: float,
    elapsed_ms: float,
    model_format: str,
) -> InspectionDecision:
    class_name = canonical_class(classification.class_name)
    if classification.confidence < threshold:
        return InspectionDecision(
            resultado="NAO_CONFORME",
            categoria="FALHA_TECNICA",
            codigo="BAIXA_CONFIANCA",
            confianca=classification.confidence,
            tempo_processamento_ms=elapsed_ms,
            formato_modelo=model_format,
        )
    code = CLASS_CODES[class_name]
    if code == "CONFORME":
        return InspectionDecision(
            resultado="CONFORME",
            categoria=None,
            codigo=None,
            confianca=classification.confidence,
            tempo_processamento_ms=elapsed_ms,
            formato_modelo=model_format,
        )
    return InspectionDecision(
        resultado="NAO_CONFORME",
        categoria="ANOMALIA_PRODUTO",
        codigo=code,
        confianca=classification.confidence,
        tempo_processamento_ms=elapsed_ms,
        formato_modelo=model_format,
    )


class InferenceEngine:
    def __init__(
        self,
        manifest: ModelManifest,
        classifier: Classifier,
    ) -> None:
        self.manifest = manifest
        self.classifier = classifier
        self.threshold = manifest.confidence_threshold

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> InferenceEngine:
        manifest = ModelManifest.load(manifest_path)
        model_path = str(manifest.resolve_model_path(manifest_path))
        classifier = UltralyticsClassifier(model_path, manifest.image_size)
        return cls(manifest, classifier)

    def inspect(self, image: Any) -> InspectionDecision:
        started = time.perf_counter()
        try:
            classification = self.classifier.predict(image)
        except Exception:
            finished = time.perf_counter()
            elapsed_ms = (finished - started) * 1000
            return InspectionDecision(
                resultado="NAO_CONFORME",
                categoria="FALHA_TECNICA",
                codigo="ERRO_INFERENCIA",
                confianca=None,
                tempo_processamento_ms=elapsed_ms,
                formato_modelo=self.manifest.format,
            )

        finished = time.perf_counter()
        elapsed_ms = (finished - started) * 1000
        return decide(
            classification,
            self.threshold,
            elapsed_ms,
            self.manifest.format,
        )
