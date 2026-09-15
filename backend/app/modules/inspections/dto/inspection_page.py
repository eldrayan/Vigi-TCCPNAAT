"""
Descrição: Representa uma página de inspeções e seus metadados de paginação.
Autor: Leôncio Ferreira
"""

from pydantic import BaseModel, Field

from .inspection_response import InspectionResponseDTO


class InspectionPageDTO(BaseModel):
    items: list[InspectionResponseDTO]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
