"""
Descrição: Representa o estado operacional publicado pelo dispositivo Edge.
Autor: Leôncio Ferreira
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ComponentStatus(StrEnum):
    """
    Descrição: Define os estados possíveis dos componentes monitorados.
    Autor: Leôncio Ferreira
    """

    ONLINE = "ONLINE"
    IDLE = "IDLE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"


class DeviceStatusDTO(BaseModel):
    """
    Descrição: Valida a conectividade, captura e processamento de uma estação.
    Autor: Leôncio Ferreira
    """

    model_config = ConfigDict(extra="forbid")

    connection: ComponentStatus
    sensor: ComponentStatus = ComponentStatus.OFFLINE
    camera: ComponentStatus
    processing: ComponentStatus
    timestamp: datetime


class DeviceStatusMessageDTO(DeviceStatusDTO):
    """
    Descrição: Valida a mensagem MQTT de estado, identificada pelo dispositivo.
    Autor: Leôncio Ferreira
    """

    device_id: str = Field(min_length=1, max_length=100)
