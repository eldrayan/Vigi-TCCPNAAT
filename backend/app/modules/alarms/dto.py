"""
Descrição: Define o contrato de resposta dos alarmes de produção.
Autor: Leôncio Ferreira
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class AlarmCreateDTO(BaseModel):
    """
    Descrição: Valida os dados de criação manual de alarme pelo operador.
    Autor: Leôncio Ferreira
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    station_id: int = Field(gt=0)
    batch_id: int = Field(gt=0)
    name: str = Field(default="Alarme de qualidade", min_length=1, max_length=100)
    threshold: float = Field(ge=0.0, le=100.0)
    alarm_type: str = "LIMITE_NAO_CONFORMIDADE"
