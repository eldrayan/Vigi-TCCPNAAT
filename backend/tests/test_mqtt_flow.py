"""
Descrição: Valida o fluxo completo do MQTT até a consulta pela API.
Autor: Leôncio Ferreira
"""

import asyncio
import json
import logging
import os
import time

import paho.mqtt.client as mqtt
import pytest
from app.infrastructure.database import Base, engine
from app.main import app, mqtt_client
from fastapi.testclient import TestClient


async def reset_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


def wait_until(predicate, timeout: float = 5) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise AssertionError("Condição não atendida dentro do tempo limite.")


@pytest.mark.skipif(
    os.getenv("VIGI_TEST_MQTT") != "1",
    reason="Teste de integração exige broker local: VIGI_TEST_MQTT=1",
)
def test_mqtt_message_is_persisted_and_exposed_by_api(caplog) -> None:
    asyncio.run(reset_database())
    caplog.set_level(logging.INFO)

    payload = {
        "inspection_id": 101,
        "timestamp": "2026-09-11T10:00:00-03:00",
        "result": "NAO_CONFORME",
        "category": "ANOMALIA_PRODUTO",
        "nonconformity_type": "TAMPA_TORTA",
        "technical_failure_type": None,
        "confidence": 0.94,
        "processing_time_ms": 180.5,
        "model_format": "pytorch",
    }

    with TestClient(app) as api:
        wait_until(mqtt_client.is_connected)

        publisher = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        publisher.connect("127.0.0.1", int(os.environ["MQTT_PORT"]))
        publisher.loop_start()
        publication = publisher.publish(
            "vigi/esteira/inspecoes",
            json.dumps(payload),
            qos=1,
        )
        publication.wait_for_publish(timeout=5)
        publisher.disconnect()
        publisher.loop_stop()

        wait_until(
            lambda: api.get("/api/inspecoes/101").status_code == 200
        )
        response = api.get("/api/inspecoes/101")
        health = api.get("/health")

    assert response.status_code == 200
    assert response.json()["nonconformity_type"] == "TAMPA_TORTA"
    assert response.json()["processing_time_ms"] == 180.5
    assert response.json()["model_format"] == "pytorch"
    assert health.status_code == 200
    assert health.json() == {
        "status": "healthy",
        "database": "connected",
        "mqtt": "connected",
    }
    assert "Inspeção 101 recebida via MQTT." in caplog.messages
    assert "Inspeção 101 persistida com sucesso." in caplog.messages
