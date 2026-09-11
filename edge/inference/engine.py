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
            result="NAO_CONFORME",
            category="FALHA_TECNICA",
            nonconformity_type=None,
            technical_failure_type="BAIXA_CONFIANCA",
            confidence=classification.confidence,
            processing_time_ms=elapsed_ms,
            model_format=model_format,
        )
    code = CLASS_CODES[class_name]
    if code == "CONFORME":
        return InspectionDecision(
            result="CONFORME",
            category=None,
            nonconformity_type=None,
            technical_failure_type=None,
            confidence=classification.confidence,
            processing_time_ms=elapsed_ms,
            model_format=model_format,
        )
    return InspectionDecision(
        result="NAO_CONFORME",
        category="ANOMALIA_PRODUTO",
        nonconformity_type=code,
        technical_failure_type=None,
        confidence=classification.confidence,
        processing_time_ms=elapsed_ms,
        model_format=model_format,
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
                result="NAO_CONFORME",
                category="FALHA_TECNICA",
                nonconformity_type=None,
                technical_failure_type="ERRO_INFERENCIA",
                confidence=None,
                processing_time_ms=elapsed_ms,
                model_format=self.manifest.format,
            )

        finished = time.perf_counter()
        elapsed_ms = (finished - started) * 1000
        return decide(
            classification,
            self.threshold,
            elapsed_ms,
            self.manifest.format,
        )
