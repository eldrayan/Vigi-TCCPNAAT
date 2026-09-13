"""Descrição: Verifica o processamento confiável das mensagens MQTT.
Autor: Leôncio Ferreira
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from app.infrastructure.mqtt.dispatcher import MQTTMessageDispatcher


def test_dispatcher_confirms_mensagem_apenas_apos_nova_tentativa(monkeypatch) -> None:
    mqtt_client = SimpleNamespace(ack=Mock())
    dispatcher = MQTTMessageDispatcher(mqtt_client)
    attempts = []

    async def handler(payload: bytes) -> None:
        assert not mqtt_client.ack.called
        attempts.append(payload)
        if len(attempts) == 1:
            raise RuntimeError("database unavailable")

    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    message = SimpleNamespace(payload=b"event", mid=7, qos=1)

    asyncio.run(dispatcher.process(message, [handler]))

    assert attempts == [b"event", b"event"]
    mqtt_client.ack.assert_called_once_with(7, 1)
