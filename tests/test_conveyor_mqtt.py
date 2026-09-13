"""Testes da sessão persistente MQTT, LWT e alarmes (RNF04)."""

from unittest.mock import MagicMock

from edge.messaging.publisher import MQTTInspectionPublisher


def test_mqtt_publisher_starts_persistent_session_with_lwt() -> None:
    mock_client = MagicMock()
    publisher = MQTTInspectionPublisher(
        host="mqtt.local",
        port=1883,
        topic="vigi/esteira/inspecoes",
        topic_alarms="vigi/esteira/alarmes",
        topic_status="vigi/esteira/status",
        client=mock_client,
        client_id="vigi-edge-test",
    )

    publisher.start_session()

    # Verifica LWT configurado
    assert mock_client.will_set.called
    will_args = mock_client.will_set.call_args
    assert will_args.kwargs["topic"] == "vigi/esteira/status"
    assert '"status": "OFFLINE"' in will_args.kwargs["payload"]
    assert will_args.kwargs["qos"] == 1
    assert will_args.kwargs["retain"] is True

    # Verifica reconexão automática <= 60s (RNF04)
    assert mock_client.reconnect_delay_set.called
    reconnect_args = mock_client.reconnect_delay_set.call_args
    assert reconnect_args.kwargs["max_delay"] <= 60

    # Verifica conexão e loop_start
    mock_client.connect.assert_called_once_with("mqtt.local", 1883)
    assert mock_client.loop_start.called

    # Verifica publicação de ONLINE
    status_publish_call = mock_client.publish.call_args_list[0]
    assert status_publish_call[0][0] == "vigi/esteira/status"
    assert '"status": "ONLINE"' in status_publish_call[0][1]


def test_mqtt_publisher_stops_session_cleanly() -> None:
    mock_client = MagicMock()
    publisher = MQTTInspectionPublisher(client=mock_client)
    publisher.start_session()

    mock_client.reset_mock()
    publisher.stop_session()

    # Ao parar, deve publicar OFFLINE formal e desconectar
    assert mock_client.publish.called
    publish_args = mock_client.publish.call_args
    assert publish_args[0][0] == "vigi/esteira/status"
    assert '"NORMAL_SHUTDOWN"' in publish_args[0][1]

    assert mock_client.disconnect.called
    assert mock_client.loop_stop.called


def test_mqtt_publisher_publish_alarm() -> None:
    mock_client = MagicMock()
    publisher = MQTTInspectionPublisher(
        topic_alarms="vigi/esteira/alarmes",
        client=mock_client,
    )

    alarm_data = {
        "inspection_id": 999,
        "alert_type": "AMASSADO",
        "severity": "WARNING",
    }
    publisher.publish_alarm(alarm_data)

    mock_client.publish.assert_called_once()
    call_args = mock_client.publish.call_args
    assert call_args[0][0] == "vigi/esteira/alarmes"
    assert '"alert_type": "AMASSADO"' in call_args[0][1]
    assert call_args.kwargs.get("qos") == 1
