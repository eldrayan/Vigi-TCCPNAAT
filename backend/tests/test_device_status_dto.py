"""
Descrição: Valida o estado operacional publicado pelo Edge.
Autor: Leôncio Ferreira
"""

from app.modules.operations.dto.device_status import DeviceStatusDTO


def test_device_status_accepts_operational_components() -> None:
    status = DeviceStatusDTO.model_validate(
        {
            "connection": "ONLINE",
            "camera": "ONLINE",
            "processing": "ONLINE",
            "timestamp": "2026-09-13T10:00:00-03:00",
        }
    )

    assert status.connection == "ONLINE"
    assert status.camera == "ONLINE"
    assert status.processing == "ONLINE"
