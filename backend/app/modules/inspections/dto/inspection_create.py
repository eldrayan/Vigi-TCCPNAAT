"""
Descrição: Valida os dados de uma inspeção recebida do edge pelo MQTT.
Autor: Leôncio Ferreira
"""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import (
    InspectionCategory,
    InspectionResult,
    NonConformityType,
    TechnicalFailureType,
)


class InspectionCreateDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    inspection_id: int = Field(gt=0)
    timestamp: datetime
    result: InspectionResult
    category: InspectionCategory | None = None
    nonconformity_type: NonConformityType | None = None
    technical_failure_type: TechnicalFailureType | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    processing_time_ms: float = Field(ge=0)
    model_format: str = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def validate_classification(self) -> Self:
        if self.result == InspectionResult.CONFORME:
            if any(
                value is not None
                for value in (
                    self.category,
                    self.nonconformity_type,
                    self.technical_failure_type,
                )
            ):
                raise ValueError(
                    "Inspeção conforme não pode possuir categoria ou tipo de falha."
                )
            return self

        if self.category == InspectionCategory.ANOMALIA_PRODUTO:
            if self.nonconformity_type is None:
                raise ValueError("Anomalia de produto deve informar o tipo.")
            if self.technical_failure_type is not None:
                raise ValueError("Anomalia de produto não pode possuir falha técnica.")
            return self

        if self.category == InspectionCategory.FALHA_TECNICA:
            if self.technical_failure_type is None:
                raise ValueError("Falha técnica deve informar o tipo.")
            if self.nonconformity_type is not None:
                raise ValueError("Falha técnica não pode possuir anomalia de produto.")
            return self

        raise ValueError("Inspeção não conforme deve informar sua categoria.")
