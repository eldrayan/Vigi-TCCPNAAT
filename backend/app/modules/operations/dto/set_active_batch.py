"""
Descrição: Valida a seleção do lote ativo de uma estação.
Autor: Leôncio Ferreira
"""

from pydantic import BaseModel, ConfigDict, Field


class SetActiveBatchDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: int = Field(gt=0)
