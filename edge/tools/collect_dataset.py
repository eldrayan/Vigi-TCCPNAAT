"""Composição e CLI do coletor de dataset."""

from __future__ import annotations

import sys

from edge.acquisition import CameraFactory, load_opencv
from edge.collection.controller import DatasetCollectionController
from edge.collection.image_store import ImageStore
from edge.collection.manifest import ManifestWriter
from edge.collection.views import create_view
from edge.config import parse_collection_config


def main(argv: list[str] | None = None) -> int:
    config = parse_collection_config(argv)
    try:
        cv2 = load_opencv()
    except RuntimeError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1

    backend = CameraFactory.resolve_backend(config.backend)
    config.output.mkdir(parents=True, exist_ok=True)
    camera = None
    controller = None
    manifest = ManifestWriter(config.output / "manifest.csv")
    view = create_view(cv2, config.headless)
    try:
        camera = CameraFactory.create(config, cv2, backend)
        image_store = ImageStore(cv2, config, backend, manifest)
        controller = DatasetCollectionController(
            config=config,
            cv2=cv2,
            camera=camera,
            view=view,
            image_store=image_store,
            backend=backend,
        )
        controller.run()
    except KeyboardInterrupt:
        print("\n[INFO] Coleta interrompida pelo usuário.")
    except RuntimeError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    finally:
        if camera is not None:
            camera.release()
        manifest.close()
        if controller is not None:
            controller.print_summary(config.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
