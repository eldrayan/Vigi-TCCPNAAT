"""
Descrição: Valida os dados necessários para cadastrar uma estação.
Autor: Leôncio Ferreira
"""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from ._normalization import normalize_code

NormalizedCode = Annotated[str, AfterValidator(normalize_code)]


class StationCreateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    code: NormalizedCode
    name: str = Field(min_length=1, max_length=100)
    device_id: NormalizedCode
