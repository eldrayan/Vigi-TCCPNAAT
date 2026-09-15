"""
Descrição: Verifica a configuração do limite de não conformidade por lote.
Autor: Leôncio Ferreira
"""

import asyncio

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


def test_dashboard_configures_batch_nonconformity_limit() -> None:
    asyncio.run(reset_database())
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        station = client.post(
            "/api/estacoes",
            json={
                "code": "envase-01",
                "name": "Estação de envase 01",
                "device_id": "leocio-raspberry",
            },
        ).json()
        batch = client.post(
            f"/api/estacoes/{station['id']}/lotes",
            json={"code": "LOTE-001"},
        ).json()
        response = client.put(
            f"/api/estacoes/{station['id']}/lotes/{batch['id']}/limite",
            json={"max_nonconformity_rate": 5.0},
        )

    assert response.status_code == 200
    assert response.json()["max_nonconformity_rate"] == 5.0
