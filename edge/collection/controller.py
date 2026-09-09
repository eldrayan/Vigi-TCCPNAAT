"""Controller do caso de uso de coleta assistida."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from edge.acquisition.camera import Camera
from edge.collection.geometry import guide_bounds
from edge.collection.image_store import ImageStore
from edge.collection.quality import sharpness_score
from edge.collection.state import CLASSES, CaptureState, class_from_key
from edge.collection.views.base import CollectionView
from edge.config import CollectionConfig


class DatasetCollectionController:
    def __init__(
        self,
        config: CollectionConfig,
        cv2: Any,
        camera: Camera,
        view: CollectionView,
        image_store: ImageStore,
        backend: str,
    ) -> None:
        self.config = config
        self.cv2 = cv2
        self.camera = camera
        self.view = view
        self.image_store = image_store
        self.backend = backend
        self.state = CaptureState(
            session_id=config.session, crop_guide=config.crop_guide
        )
        self.last_burst_capture = 0.0
        self.last_manual_capture = 0.0

    def run(self) -> None:
        print(f"[OK] Câmera aberta com backend {self.backend}.")
        print(f"[OK] Sessão: {self.state.session_id}")
        print("[INFO] Pressione Q ou ESC para encerrar com segurança.")
        try:
            self.view.open()
            while True:
                ok, frame = self.camera.read()
                if not ok or frame is None:
                    raise RuntimeError("A câmera parou de fornecer imagens.")

                guide = guide_bounds(
                    frame_width=frame.shape[1],
                    frame_height=frame.shape[0],
                    width_ratio=self.config.guide_width,
                    height_ratio=self.config.guide_height,
                )
                score = sharpness_score(self.cv2, frame)
                self.view.render(
                    frame=frame,
                    state=self.state,
                    guide=guide,
                    score=score,
                    threshold=self.config.blur_threshold,
                    message="",
                )
                key = self.view.read_key()
                if self._handle_control_key(key):
                    break
                self._capture_when_requested(key, frame, guide, score)
        finally:
            self.state.burst_enabled = False
            self.view.close()

    def _handle_control_key(self, key: int) -> bool:
        selected = class_from_key(key)
        if selected is not None:
            self.state.select_class(selected)
            self.view.notify("INFO", f"Classe selecionada: {self.state.class_name}")
        elif key in (ord("q"), ord("Q"), 27):
            return True
        elif key in (ord("b"), ord("B")):
            self.state.burst_enabled = not self.state.burst_enabled
            self.last_burst_capture = 0.0
            message = "Burst ligado" if self.state.burst_enabled else "Burst desligado"
            self.view.notify("INFO", message)
        elif key in (ord("n"), ord("N")):
            self.state.next_physical_sample()
            self.view.notify(
                "INFO", f"Novo frasco físico: {self.state.physical_sample:03d}"
            )
        elif key in (ord("c"), ord("C")):
            self.state.crop_guide = not self.state.crop_guide
            message = (
                "Recorte da guia ligado"
                if self.state.crop_guide
                else "Quadro inteiro"
            )
            self.view.notify("INFO", message)
        return False

    def _capture_when_requested(
        self,
        key: int,
        frame: Any,
        guide: tuple[int, int, int, int],
        score: float,
    ) -> None:
        now = time.monotonic()
        manual_requested = key == ord(" ") and now - self.last_manual_capture >= 0.25
        burst_requested = (
            self.state.burst_enabled
            and now - self.last_burst_capture >= self.config.burst_interval
        )
        if not manual_requested and not burst_requested:
            return

        if manual_requested:
            self.last_manual_capture = now
        if burst_requested:
            self.last_burst_capture = now

        if self.config.blur_threshold > 0 and score < self.config.blur_threshold:
            self.state.rejected_blurry += 1
            self.view.notify("CAPTURA", f"Descartada: desfocada ({score:.1f})")
            return

        mode = "manual" if manual_requested else "burst"
        path = self.image_store.save(frame, self.state, guide, score, mode)
        self.view.notify("CAPTURA", f"Salva: {path.name}")

    def print_summary(self, output: Path) -> None:
        print("\nResumo da coleta")
        print(f"  Sessão: {self.state.session_id}")
        for class_id, class_name in CLASSES.items():
            print(f"  {class_id} - {class_name}: {self.state.saved_by_class[class_id]}")
        print(f"  Rejeitadas por desfoque: {self.state.rejected_blurry}")
        print(f"  Saída: {output.resolve()}")
