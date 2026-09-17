"""
Descrição: Valida o estado operacional publicado pelo Edge.
Autor: Leôncio Ferreira
"""

from app.modules.operations.dto.device_status import (
    DeviceStatusDTO,
    DeviceStatusMessageDTO,
)


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


def test_device_status_message_normalizes_legacy_device_id() -> None:
    message = DeviceStatusMessageDTO.model_validate(
        {
            "device_id": "ESTACAO_01",
            "connection": "ONLINE",
            "camera": "ONLINE",
            "processing": "IDLE",
            "timestamp": "2026-09-16T20:02:20+00:00",
        }
    )

    assert message.device_id == "estacao-01"
