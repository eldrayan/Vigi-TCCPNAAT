"""
Descrição: Define os valores válidos para resultados e falhas de inspeção.
Autor: Leôncio Ferreira
"""

from enum import StrEnum


class InspectionResult(StrEnum):
    CONFORME = "CONFORME"
    NAO_CONFORME = "NAO_CONFORME"


class InspectionCategory(StrEnum):
    ANOMALIA_PRODUTO = "ANOMALIA_PRODUTO"
    FALHA_TECNICA = "FALHA_TECNICA"


class NonConformityType(StrEnum):
    SEM_TAMPA = "SEM_TAMPA"
    TAMPA_TORTA = "TAMPA_TORTA"
    AMASSADO = "AMASSADO"


class TechnicalFailureType(StrEnum):
    ERRO_CAPTURA = "ERRO_CAPTURA"
    BAIXA_CONFIANCA = "BAIXA_CONFIANCA"
    ERRO_INFERENCIA = "ERRO_INFERENCIA"
