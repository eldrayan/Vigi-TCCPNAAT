"""
Descrição: Representa os totais consolidados das inspeções armazenadas.
Autor: Leôncio Ferreira
"""

from pydantic import BaseModel


class InspectionSummaryDTO(BaseModel):
    total: int
    compliant: int
    noncompliant: int
    compliance_rate: float
    sem_tampa: int
    tampa_torta: int
    amassado: int
    falha_tecnica: int
