"""Testes do servidor HTTP usado para ajustar o enquadramento."""

from __future__ import annotations

import errno
import sys

from scripts import preview_camera


def test_busy_port_is_reported_before_opening_camera(monkeypatch) -> None:
    camera_opened = False

    def busy_server(*_args, **_kwargs):
        raise OSError(errno.EADDRINUSE, "Address already in use")

    def open_camera(*_args, **_kwargs):
        nonlocal camera_opened
        camera_opened = True

    monkeypatch.setattr(preview_camera, "StreamingServer", busy_server)
    monkeypatch.setattr(preview_camera, "create_camera", open_camera)
    monkeypatch.setattr(sys, "argv", ["preview_camera.py", "--port", "8090"])

    assert preview_camera.main() == 2
    assert camera_opened is False
