"""Valida os dados necessários para abrir um lote."""

from pydantic import BaseModel, ConfigDict, Field


class BatchCreateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    code: str = Field(min_length=1, max_length=100)
