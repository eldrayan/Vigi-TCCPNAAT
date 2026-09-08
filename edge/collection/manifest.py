"""Persistência incremental dos metadados da coleta."""

from __future__ import annotations

import csv
import os
from pathlib import Path


MANIFEST_FIELDS = (
    "arquivo",
    "classe",
    "sessao",
    "amostra_fisica",
    "grupo",
    "capturado_em_utc",
    "backend",
    "largura",
    "altura",
    "recortada",
    "nitidez",
    "modo",
)


class ManifestWriter:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        new_file = not path.exists() or path.stat().st_size == 0
        self.handle = path.open("a", encoding="utf-8", newline="")
        self.writer = csv.DictWriter(self.handle, fieldnames=MANIFEST_FIELDS)
        if new_file:
            self.writer.writeheader()
            self._sync()

    def append(self, row: dict[str, object]) -> None:
        self.writer.writerow(row)
        self._sync()

    def _sync(self) -> None:
        self.handle.flush()
        os.fsync(self.handle.fileno())

    def close(self) -> None:
        self.handle.close()

    def __enter__(self) -> "ManifestWriter":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
