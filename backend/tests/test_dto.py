"""
Descrição: Verifica o contrato e as regras dos DTOs de inspeção.
Autor: Leôncio Ferreira
"""

import pytest
from app.modules.inspections.dto import InspectionCreateDTO
from pydantic import ValidationError


def inspection_payload(**changes) -> dict:
    payload = {
        "inspection_id": 1,
        "timestamp": "2026-09-11T10:00:00-03:00",
        "result": "CONFORME",
        "category": None,
        "nonconformity_type": None,
        "technical_failure_type": None,
        "confidence": 0.98,
        "processing_time_ms": 150.5,
        "model_format": "pytorch",
    }
    return payload | changes


def test_accepts_compliant_inspection() -> None:
    dto = InspectionCreateDTO.model_validate(inspection_payload())

    assert dto.inspection_id == 1
    assert dto.result == "CONFORME"
    assert dto.processing_time_ms == 150.5
    assert dto.model_format == "pytorch"


def test_accepts_product_anomaly_with_exact_type() -> None:
    dto = InspectionCreateDTO.model_validate(
        inspection_payload(
            result="NAO_CONFORME",
            category="ANOMALIA_PRODUTO",
            nonconformity_type="SEM_TAMPA",
        )
    )

    assert dto.nonconformity_type == "SEM_TAMPA"


def test_rejects_product_anomaly_without_type() -> None:
    with pytest.raises(ValidationError, match="deve informar o tipo"):
        InspectionCreateDTO.model_validate(
            inspection_payload(
                result="NAO_CONFORME",
                category="ANOMALIA_PRODUTO",
            )
        )


def test_rejects_technical_failure_mixed_with_product_anomaly() -> None:
    with pytest.raises(ValidationError, match="não pode possuir anomalia"):
        InspectionCreateDTO.model_validate(
            inspection_payload(
                result="NAO_CONFORME",
                category="FALHA_TECNICA",
                nonconformity_type="AMASSADO",
                technical_failure_type="ERRO_INFERENCIA",
            )
        )


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_rejects_confidence_outside_probability_range(confidence: float) -> None:
    with pytest.raises(ValidationError):
        InspectionCreateDTO.model_validate(
            inspection_payload(confidence=confidence)
        )
