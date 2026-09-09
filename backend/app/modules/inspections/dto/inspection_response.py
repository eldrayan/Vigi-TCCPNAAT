"""
Descrição: Representa uma inspeção persistida e devolvida pela API.
Autor: Leôncio Ferreira
"""

from datetime import datetime

from pydantic import ConfigDict

from .inspection_create import InspectionCreateDTO


class InspectionResponseDTO(InspectionCreateDTO):
    model_config = ConfigDict(from_attributes=True)
    recebido_em: datetime
