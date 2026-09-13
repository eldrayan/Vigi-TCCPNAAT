"""Representa a configuração operacional entregue ao dispositivo Edge."""

from pydantic import BaseModel, ConfigDict, Field


class OperationalContextDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    station_code: str = Field(min_length=1, max_length=50)
    batch_code: str = Field(min_length=1, max_length=100)

    @property
    def inspections_topic(self) -> str:
        return f"vigi/estacoes/{self.station_code}/inspecoes"
