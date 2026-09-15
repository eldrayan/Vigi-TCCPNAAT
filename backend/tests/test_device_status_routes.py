"""
Descrição: Verifica a consulta HTTP do estado atual do dispositivo.
Autor: Leôncio Ferreira
"""

import asyncio
from datetime import datetime

from app.infrastructure.database import Base, SessionFactory, engine, get_session
from app.modules.operations.dto import DeviceStatusDTO, StationCreateDTO
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.routes import router
from app.modules.operations.service import OperationsService
from fastapi import FastAPI
from fastapi.testclient import TestClient


async def reset_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def override_session():
    async with SessionFactory() as session:
        yield session


def test_dashboard_can_consult_device_status() -> None:
    asyncio.run(reset_database())
    service = OperationsService(OperationsRepository())

    async def prepare() -> int:
        async with SessionFactory() as session:
            station = await service.create_station(
                session,
                StationCreateDTO(
                    code="envase-01",
                    name="Estação de envase 01",
                    device_id="leocio-raspberry",
                ),
            )
            await service.report_device_status(
                session,
                "leocio-raspberry",
                DeviceStatusDTO(
                    connection="ONLINE",
                    camera="ONLINE",
                    processing="ONLINE",
                    timestamp=datetime.fromisoformat("2026-09-13T10:00:00-03:00"),
                ),
            )
            return station.id

    station_id = asyncio.run(prepare())
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        response = client.get(f"/api/estacoes/{station_id}/status")

    assert response.status_code == 200
    assert response.json()["connection"] == "ONLINE"
    assert response.json()["camera"] == "ONLINE"
