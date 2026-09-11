"""Contrato versionado dos artefatos de classificacao."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from numbers import Real
from pathlib import Path

from .inspection_classes import CLASS_NAMES

SUPPORTED_FORMATS = {"pytorch"}
REQUIRED_METRICS = ("accuracy", "false_negative_rate", "false_positive_rate")


def _probability(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field} deve ser um numero real")
    number = float(value)
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError(f"{field} deve ser finito e estar entre 0 e 1")
    return number


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
        if not isinstance(self.model_path, str) or not self.model_path:
            raise ValueError("model_path deve ser uma string nao vazia")
        model_path = Path(self.model_path)
        if model_path.is_absolute() or ".." in model_path.parts:
            raise ValueError(
                "model_path deve permanecer dentro do diretorio do manifesto"
            )
        if model_path.suffix.lower() != ".pt":
            raise ValueError("Modelos PyTorch devem usar a extensao .pt")
        if self.classes != CLASS_NAMES:
            raise ValueError("As classes do manifesto divergem das classes oficiais")
        _probability(self.confidence_threshold, "confidence_threshold")
        if (
            isinstance(self.image_size, bool)
            or not isinstance(self.image_size, int)
            or self.image_size <= 0
        ):
            raise ValueError("image_size deve ser positivo")
        if not isinstance(self.dataset_hash, str) or not self.dataset_hash:
            raise ValueError("dataset_hash deve ser uma string nao vazia")
        if not isinstance(self.ultralytics_version, str):
            raise ValueError("ultralytics_version deve ser uma string")
        if not isinstance(self.metrics, dict):
            raise ValueError("metrics deve ser um objeto")
        for field in REQUIRED_METRICS:
            if field not in self.metrics:
                raise ValueError(f"Metrica obrigatoria ausente: {field}")
            _probability(self.metrics[field], field)

    @classmethod
    def load(cls, path: Path) -> ModelManifest:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("A raiz do manifesto deve ser um objeto JSON")
        if not isinstance(data.get("classes"), list):
            raise ValueError("classes deve ser uma lista")
        data["classes"] = tuple(data["classes"])
        manifest = cls(**data)
        model_path = Path(manifest.model_path)
        if not model_path.is_absolute():
            model_path = path.parent / model_path
        if not model_path.is_file():
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
