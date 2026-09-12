"""
Descrição: Exporta os contratos de entrada e saída do módulo de inspeções.
Autor: Leôncio Ferreira
"""

from .enums import (
    InspectionCategory,
    InspectionResult,
    NonConformityType,
    TechnicalFailureType,
)
from .inspection_create import InspectionCreateDTO
from .inspection_response import InspectionResponseDTO
from .inspection_summary import InspectionSummaryDTO

__all__ = [
    "InspectionCategory",
    "InspectionCreateDTO",
    "InspectionResponseDTO",
    "InspectionSummaryDTO",
    "InspectionResult",
    "NonConformityType",
    "TechnicalFailureType",
]
