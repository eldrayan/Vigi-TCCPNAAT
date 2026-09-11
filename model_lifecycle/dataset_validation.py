"""Validacao do dataset."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

from .inspection_classes import CLASS_NAMES

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLITS = ("train", "val", "test")


@dataclass(frozen=True)
class DatasetReport:
    root: str
    counts: dict[str, dict[str, int]]
    total_images: int
    duplicate_hashes: dict[str, list[str]]
    errors: list[str]
    warnings: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["valid"] = self.valid
        return data


def _image_paths(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_hash(root: Path) -> str:
    """Calcula um identificador deterministico pelo caminho e conteudo das imagens."""
    digest = hashlib.sha256()
    for path in sorted(
        item
        for item in root.rglob("*")
        if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES
    ):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(_sha256(path).encode())
    return digest.hexdigest()


def _verify_image(path: Path) -> str | None:
    try:
        from PIL import Image

        with Image.open(path) as image:
            image.verify()
    except Exception as exc:
        return f"Imagem invalida {path}: {exc}"
    return None


def validate_dataset(root: Path, verify_images: bool = True) -> DatasetReport:
    """Valida estrutura, imagens e vazamento exato sem alterar o dataset."""
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, dict[str, int]] = {}
    hashes: dict[str, list[tuple[str, Path]]] = {}

    if not root.is_dir():
        errors.append(f"Dataset nao encontrado: {root}")

    for split in SPLITS:
        split_dir = root / split
        counts[split] = {}
        if not split_dir.is_dir():
            errors.append(f"Split ausente: {split_dir}")
            continue

        actual_classes = {path.name for path in split_dir.iterdir() if path.is_dir()}
        missing = set(CLASS_NAMES) - actual_classes
        unexpected = actual_classes - set(CLASS_NAMES)
        if missing:
            errors.append(f"Classes ausentes em {split}: {', '.join(sorted(missing))}")
        if unexpected:
            errors.append(
                f"Classes inesperadas em {split}: {', '.join(sorted(unexpected))}"
            )

        for class_name in CLASS_NAMES:
            paths = _image_paths(split_dir / class_name)
            counts[split][class_name] = len(paths)
            if not paths:
                errors.append(f"Classe vazia: {split}/{class_name}")
            for path in paths:
                if verify_images:
                    problem = _verify_image(path)
                    if problem:
                        errors.append(problem)
                file_hash = _sha256(path)
                hashes.setdefault(file_hash, []).append((split, path))

    duplicate_hashes: dict[str, list[str]] = {}
    for file_hash, occurrences in hashes.items():
        occurrence_splits = {split for split, _ in occurrences}
        if len(occurrence_splits) > 1:
            paths = [str(path.relative_to(root)) for _, path in occurrences]
            duplicate_hashes[file_hash] = paths
            errors.append(
                "Imagem identica presente em splits diferentes: " + ", ".join(paths)
            )

    total_images = sum(sum(class_counts.values()) for class_counts in counts.values())
    if total_images and total_images < 200:
        warnings.append(
            "O dataset inteiro possui menos de 200 imagens; a homologacao estatistica "
            "dos RNF06/RNF07 pode permanecer pendente."
        )

    return DatasetReport(
        root=str(root),
        counts=counts,
        total_images=total_images,
        duplicate_hashes=duplicate_hashes,
        errors=errors,
        warnings=warnings,
    )
