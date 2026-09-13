"""
Descrição: Valida o limite percentual de não conformidades configurado no lote.
Autor: Leôncio Ferreira
"""

from pydantic import BaseModel, ConfigDict, Field


class SetNonconformityLimitDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_nonconformity_rate: float = Field(ge=0, le=100)
