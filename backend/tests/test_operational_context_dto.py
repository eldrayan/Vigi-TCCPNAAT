"""Valida os contratos de estação, lote e contexto operacional."""

import pytest
from app.modules.operations.dto import (
    BatchCreateDTO,
    OperationalContextDTO,
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
