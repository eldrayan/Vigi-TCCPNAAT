"""
Descrição: Define o contrato de resposta dos alarmes de produção.
Autor: Leôncio Ferreira
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlarmResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    station_id: int
    batch_id: int
    alarm_type: str
    name: str
    rate: float
    threshold: float
    status: str
    created_at: datetime
    acknowledged_at: datetime | None
    acknowledged_by: str | None


class AcknowledgeAlarmDTO(BaseModel):
    """
    Descrição: Valida a identificação do responsável pelo reconhecimento.
    Autor: Leôncio Ferreira
    """

    acknowledged_by: str
