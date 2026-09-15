"""Valida a publicação persistente do estado do dispositivo pelo Edge."""

import json

from edge.messaging.status import MQTTDeviceStatusPublisher


class ClientStub:
    def __init__(self) -> None:
        self.will = None
        self.publications: list[tuple[str, str, int, bool]] = []

    def will_set(self, topic: str, payload: str, qos: int, retain: bool) -> None:
        self.will = (topic, json.loads(payload), qos, retain)

    def connect(self, host: str, port: int) -> None:
        self.connection = (host, port)

    def loop_start(self) -> None:
        return None

    def publish(self, topic: str, payload: str, qos: int, retain: bool):
        self.publications.append((topic, payload, qos, retain))
        return PublicationStub()

    def disconnect(self) -> None:
        return None

    def loop_stop(self) -> None:
        return None


class PublicationStub:
    def wait_for_publish(self, timeout: float) -> None:
        return None

    def is_published(self) -> bool:
        return True


def test_status_publisher_uses_lwt_and_retains_current_state() -> None:
    client = ClientStub()
    publisher = MQTTDeviceStatusPublisher(
        host="mqtt.local", device_id="leocio-raspberry", client=client
    )

    publisher.start(camera="ONLINE", processing="ONLINE")
    publisher.stop()

    assert client.will[0] == "vigi/dispositivos/leocio-raspberry/status"
    assert client.will[1]["device_id"] == "leocio-raspberry"
    assert client.will[1]["connection"] == "OFFLINE"
    assert client.will[1]["sensor"] == "OFFLINE"
    assert client.will[1]["camera"] == "OFFLINE"
    assert client.will[1]["processing"] == "OFFLINE"
    assert "timestamp" in client.will[1]
    assert client.will[2:] == (1, True)
    online = json.loads(client.publications[0][1])
    offline = json.loads(client.publications[1][1])
    assert online["connection"] == "ONLINE"
    assert online["sensor"] == "ONLINE"
    assert online["camera"] == "ONLINE"
    assert offline["connection"] == "OFFLINE"
    assert offline["sensor"] == "OFFLINE"
    assert client.publications[0][2:] == (1, True)
