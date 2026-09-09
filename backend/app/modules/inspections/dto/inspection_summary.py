"""
Descrição: Representa os totais consolidados das inspeções armazenadas.
Autor: Leôncio Ferreira
"""

from pydantic import BaseModel


class InspectionSummaryDTO(BaseModel):
    total: int
    conformes: int
    nao_conformes: int
