"""Verifica a configuração de autenticação da conexão MQTT."""

from unittest.mock import Mock

from app.config import Settings
from app.infrastructure.mqtt.connection import MQTTConnection


def test_configures_mqtt_credentials(monkeypatch):
    paho_client = Mock()
    client_factory = Mock(return_value=paho_client)
    monkeypatch.setattr(
        "app.infrastructure.mqtt.connection.mqtt.Client",
        client_factory,
    )

    MQTTConnection(
        Settings(
            _env_file=None,
            mqtt_username="vigi-backend",
            mqtt_password="secret",
        )
    )

    paho_client.username_pw_set.assert_called_once_with(
        "vigi-backend",
        "secret",
    )


def test_keeps_anonymous_connection_when_username_is_absent(monkeypatch):
    paho_client = Mock()
    client_factory = Mock(return_value=paho_client)
    monkeypatch.setattr(
        "app.infrastructure.mqtt.connection.mqtt.Client",
        client_factory,
    )

    MQTTConnection(Settings(_env_file=None))

    paho_client.username_pw_set.assert_not_called()
