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

    id_inspecao: int = Field(gt=0)
    timestamp: datetime
    resultado: InspectionResult
    categoria: InspectionCategory | None = None
    tipo_nao_conformidade: NonConformityType | None = None
    tipo_falha_tecnica: TechnicalFailureType | None = None
    confianca: float | None = Field(default=None, ge=0, le=1)
    tempo_processamento_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_classification(self) -> Self:
        if self.resultado == InspectionResult.CONFORME:
            if any(
                value is not None
                for value in (
                    self.categoria,
                    self.tipo_nao_conformidade,
                    self.tipo_falha_tecnica,
                )
            ):
                raise ValueError(
                    "Inspeção conforme não pode possuir categoria ou tipo de falha."
                )
            return self

        if self.categoria == InspectionCategory.ANOMALIA_PRODUTO:
            if self.tipo_nao_conformidade is None:
                raise ValueError("Anomalia de produto deve informar o tipo.")
            if self.tipo_falha_tecnica is not None:
                raise ValueError("Anomalia de produto não pode possuir falha técnica.")
            return self

        if self.categoria == InspectionCategory.FALHA_TECNICA:
            if self.tipo_falha_tecnica is None:
                raise ValueError("Falha técnica deve informar o tipo.")
            if self.tipo_nao_conformidade is not None:
                raise ValueError("Falha técnica não pode possuir anomalia de produto.")
            return self

        raise ValueError("Inspeção não conforme deve informar sua categoria.")
