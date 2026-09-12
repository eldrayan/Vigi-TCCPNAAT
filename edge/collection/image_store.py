"""Armazenamento atômico das imagens e dos respectivos metadados."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from edge.collection.manifest import ManifestWriter
from edge.collection.state import CaptureState
from edge.config import CollectionConfig


class ImageStore:
    def __init__(
        self,
        cv2: Any,
        config: CollectionConfig,
        backend: str,
        manifest: ManifestWriter,
    ) -> None:
        self.cv2 = cv2
        self.config = config
        self.backend = backend
        self.manifest = manifest

    def save(
        self,
        frame: Any,
        state: CaptureState,
        guide: tuple[int, int, int, int],
        score: float,
        mode: str,
    ) -> Path:
        image = frame
        if state.crop_guide:
            x1, y1, x2, y2 = guide
            image = frame[y1:y2, x1:x2]

        captured_at = datetime.now(UTC)
        class_dir = self.config.output / state.class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        sequence = state.saved_by_class[state.selected_class] + 1
        timestamp = captured_at.strftime("%Y%m%dT%H%M%S_%fZ")
        filename = f"{state.group_id}__{timestamp}__{sequence:05d}.jpg"
        path = class_dir / filename
        temporary_path = class_dir / f".{filename}.tmp.jpg"

        written = self.cv2.imwrite(
            str(temporary_path),
            image,
            [self.cv2.IMWRITE_JPEG_QUALITY, self.config.jpeg_quality],
        )
        if not written:
            raise RuntimeError(f"Não foi possível gravar a imagem {path}.")
        os.replace(temporary_path, path)

        state.saved_by_class[state.selected_class] = sequence
        self.manifest.append(
            {
                "arquivo": path.relative_to(self.config.output).as_posix(),
                "classe": state.class_name,
                "sessao": state.session_id,
                "amostra_fisica": state.physical_sample,
                "grupo": state.group_id,
                "capturado_em_utc": captured_at.isoformat(),
                "backend": self.backend,
                "largura": int(image.shape[1]),
                "altura": int(image.shape[0]),
                "recortada": state.crop_guide,
                "nitidez": f"{score:.2f}",
                "modo": mode,
            }
        )
        return path
