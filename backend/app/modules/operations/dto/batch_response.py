"""
Descrição: Representa um lote retornado pela API.
Autor: Leôncio Ferreira
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BatchResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    station_id: int
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    max_nonconformity_rate: float | None
    alarm_name: str | None
