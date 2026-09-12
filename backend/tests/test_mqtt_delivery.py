"""Descrição: Verifica confirmação MQTT somente após persistência.
Autor: Leôncio Ferreira
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from app.config import Settings
from app.infrastructure.mqtt.client import MQTTClient


def test_ack_after_retry(monkeypatch):
    client = MQTTClient(Settings())
    client.client.ack = Mock()
    attempts = []

    async def handler(payload):
        assert not client.client.ack.called
        attempts.append(payload)
        if len(attempts) == 1:
            raise RuntimeError("database unavailable")

    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    message = SimpleNamespace(payload=b"event", mid=7, qos=1)
    asyncio.run(client._process(message, [handler]))
    assert len(attempts) == 2
    client.client.ack.assert_called_once_with(7, 1)
