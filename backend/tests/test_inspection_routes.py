"""
Descrição: Verifica o contrato HTTP das rotas de consulta de inspeções.
Autor: Leôncio Ferreira
"""

from app.main import app


def test_list_inspections_exposes_optional_filters_in_query() -> None:
    parameters = app.openapi()["paths"]["/api/inspecoes"]["get"]["parameters"]
    parameter_names = {parameter["name"] for parameter in parameters}

    assert "filters" not in parameter_names
    assert {
        "station_code",
        "batch_code",
        "result",
        "nonconformity_type",
    } <= parameter_names


def test_list_inspections_exposes_pagination_metadata() -> None:
    document = app.openapi()
    schema = document["paths"]["/api/inspecoes"]["get"]["responses"]["200"]
    reference = schema["content"]["application/json"]["schema"]["$ref"]
    page_schema = document["components"]["schemas"][reference.rsplit("/", 1)[-1]]

    assert {"items", "total", "limit", "offset"} <= page_schema["properties"].keys()
