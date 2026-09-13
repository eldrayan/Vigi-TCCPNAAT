"""
Descrição: Representa o estado operacional publicado pelo dispositivo Edge.
Autor: Leôncio Ferreira
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ComponentStatus(StrEnum):
    """Define os estados possíveis dos componentes monitorados."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"


class DeviceStatusDTO(BaseModel):
    """Valida a conectividade, captura e processamento de uma estação."""

    model_config = ConfigDict(extra="forbid")

    connection: ComponentStatus
    camera: ComponentStatus
    processing: ComponentStatus
    timestamp: datetime


class DeviceStatusMessageDTO(DeviceStatusDTO):
    """Valida a mensagem MQTT de estado, identificada pelo dispositivo."""

    device_id: str = Field(min_length=1, max_length=100)
