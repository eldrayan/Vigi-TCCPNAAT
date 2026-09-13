"""Valida as rotas usadas pelo dashboard para configurar a operação."""

import asyncio
from unittest.mock import Mock

from app.infrastructure.database import Base, SessionFactory, engine, get_session
from app.modules.operations.routes import router
from fastapi import FastAPI
from fastapi.testclient import TestClient


async def reset_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def override_session():
    async with SessionFactory() as session:
        yield session


def test_dashboard_can_configure_station_and_active_batch() -> None:
    asyncio.run(reset_database())
    producer = Mock()
    app = FastAPI()
    app.state.mqtt_producer = producer
    app.include_router(router)
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        station = client.post(
            "/api/estacoes",
            json={
                "code": "Envase 01",
                "name": "Estação de envase 01",
                "device_id": "leocio-raspberry",
            },
        )
        station_id = station.json()["id"]
        first = client.post(
            f"/api/estacoes/{station_id}/lotes", json={"code": "LOTE-001"}
        )
        second = client.post(
            f"/api/estacoes/{station_id}/lotes", json={"code": "LOTE-002"}
        )
        context = client.put(
            f"/api/estacoes/{station_id}/lote-ativo",
            json={"batch_id": second.json()["id"]},
        )

    assert station.status_code == 201
    assert first.status_code == 201
    assert context.status_code == 200
    assert context.json() == {
        "station_code": "envase-01",
        "batch_code": "LOTE-002",
    }
    producer.publish.assert_called_once_with(
        topic="vigi/dispositivos/leocio-raspberry/configuracao",
        payload={"station_code": "envase-01", "batch_code": "LOTE-002"},
        qos=1,
        retain=True,
    )
