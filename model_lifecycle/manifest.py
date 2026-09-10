"""Contrato versionado dos artefatos de classificacao."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .inspection_classes import CLASS_NAMES

SUPPORTED_FORMATS = {"pytorch", "tflite"}


@dataclass(frozen=True)
class ModelManifest:
    model_path: str
    format: str
    classes: tuple[str, ...]
    confidence_threshold: float
    image_size: int
    dataset_hash: str
    ultralytics_version: str
    metrics: dict[str, float]

    def __post_init__(self) -> None:
        if self.format not in SUPPORTED_FORMATS:
            raise ValueError(f"Formato nao suportado: {self.format}")
        if self.classes != CLASS_NAMES:
            raise ValueError("As classes do manifesto divergem das classes oficiais")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold deve estar entre 0 e 1")
        if self.image_size <= 0:
            raise ValueError("image_size deve ser positivo")

    @classmethod
    def load(cls, path: Path) -> ModelManifest:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["classes"] = tuple(data["classes"])
        manifest = cls(**data)
        model_path = Path(manifest.model_path)
        if not model_path.is_absolute():
            model_path = path.parent / model_path
        if not model_path.exists():
            raise ValueError(f"Modelo referenciado nao encontrado: {model_path}")
        return manifest

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def resolve_model_path(self, manifest_path: Path) -> Path:
        model_path = Path(self.model_path)
        return (
            model_path
            if model_path.is_absolute()
            else manifest_path.parent / model_path
        )
