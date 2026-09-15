"""
Descrição: Valida os contratos de estação, lote e contexto operacional.
Autor: Leôncio Ferreira
"""

import pytest
from app.modules.operations.dto import (
    BatchCreateDTO,
    OperationalContextDTO,
    SetNonconformityLimitDTO,
    StationCreateDTO,
)
from pydantic import ValidationError


def test_station_normalizes_code() -> None:
    dto = StationCreateDTO(
        code=" Envase 01 ",
        name="Estação de envase 01",
        device_id=" leocio-raspberry ",
    )

    assert dto.code == "envase-01"
    assert dto.device_id == "leocio-raspberry"


def test_batch_rejects_empty_code() -> None:
    with pytest.raises(ValidationError):
        BatchCreateDTO(code="   ")


def test_operational_context_builds_station_topic() -> None:
    dto = OperationalContextDTO(
        station_code="envase-01",
        batch_code="LOTE-2026-001",
    )

    assert dto.inspections_topic == "vigi/estacoes/envase-01/inspecoes"


def test_alarm_configuration_accepts_name_and_limit() -> None:
    dto = SetNonconformityLimitDTO(
        alarm_name="Qualidade do lote",
        max_nonconformity_rate=15,
    )

    assert dto.alarm_name == "Qualidade do lote"
    assert dto.max_nonconformity_rate == 15
