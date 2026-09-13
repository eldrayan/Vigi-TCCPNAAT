"""Valida os filtros disponíveis nas consultas de inspeções."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import InspectionResult, NonConformityType


class InspectionFilterDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    station_code: str | None = Field(default=None, min_length=1, max_length=50)
    batch_code: str | None = Field(default=None, min_length=1, max_length=100)
    result: InspectionResult | None = None
    nonconformity_type: NonConformityType | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        if self.start_at and self.end_at and self.start_at > self.end_at:
            raise ValueError("O início do período deve ser anterior ao fim.")
        return self
