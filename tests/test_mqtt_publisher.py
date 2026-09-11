"""Testes da composição e publicação de eventos de inspeção no MQTT."""

from datetime import UTC, datetime

from edge.inference.schemas import InspectionDecision
from edge.messaging import InspectionEvent, MQTTInspectionPublisher
from scripts import infer


class Publication:
    def __init__(self) -> None:
        self.wait_timeout: float | None = None

    def wait_for_publish(self, timeout: float) -> None:
        self.wait_timeout = timeout

    def is_published(self) -> bool:
        return True


class MQTTClientStub:
    def __init__(self) -> None:
        self.connected_to: tuple[str, int] | None = None
        self.publication = Publication()
        self.published: tuple[str, str, int, bool] | None = None
        self.loop_started = False
        self.disconnected = False
        self.loop_stopped = False

    def connect(self, host: str, port: int) -> None:
        self.connected_to = (host, port)

    def loop_start(self) -> None:
        self.loop_started = True

    def publish(
        self,
        topic: str,
        payload: str,
        qos: int,
        retain: bool,
    ) -> Publication:
        self.published = (topic, payload, qos, retain)
        return self.publication

    def disconnect(self) -> None:
        self.disconnected = True

    def loop_stop(self) -> None:
        self.loop_stopped = True


def decision() -> InspectionDecision:
    return InspectionDecision(
        result="NAO_CONFORME",
        category="ANOMALIA_PRODUTO",
        nonconformity_type="SEM_TAMPA",
        technical_failure_type=None,
        confidence=0.94,
        processing_time_ms=180.5,
        model_format="pytorch",
    )


def test_event_adds_identifier_and_timestamp_to_decision() -> None:
    timestamp = datetime(2026, 9, 11, 15, 0, tzinfo=UTC)

    event = InspectionEvent.from_decision(
        decision(),
        timestamp=timestamp,
        inspection_id=123,
    )

    assert event.as_dict() == {
        "inspection_id": 123,
        "timestamp": "2026-09-11T15:00:00+00:00",
        "result": "NAO_CONFORME",
        "category": "ANOMALIA_PRODUTO",
        "nonconformity_type": "SEM_TAMPA",
        "technical_failure_type": None,
        "confidence": 0.94,
        "processing_time_ms": 180.5,
        "model_format": "pytorch",
    }


def test_publisher_sends_event_with_qos_one() -> None:
    client = MQTTClientStub()
    event = InspectionEvent.from_decision(
        decision(),
        timestamp=datetime(2026, 9, 11, 15, 0, tzinfo=UTC),
        inspection_id=123,
    )
    publisher = MQTTInspectionPublisher(
        host="mqtt.local",
        port=1883,
        topic="vigi/esteira/inspecoes",
        client=client,
    )

    publisher.publish(event)

    assert client.connected_to == ("mqtt.local", 1883)
    assert client.loop_started
    assert client.published is not None
    assert client.published[0] == "vigi/esteira/inspecoes"
    assert '"inspection_id": 123' in client.published[1]
    assert client.published[2:] == (1, False)
    assert client.publication.wait_timeout == 5
    assert client.disconnected
    assert client.loop_stopped


def test_inference_cli_publishes_complete_event(monkeypatch, tmp_path) -> None:
    image = tmp_path / "sample.jpg"
    image.write_bytes(b"imagem simulada")
    published: list[InspectionEvent] = []

    class EngineStub:
        def inspect(self, source: str) -> InspectionDecision:
            assert source == str(image)
            return decision()

    class PublisherStub:
        def __init__(self, host: str, port: int, topic: str) -> None:
            assert (host, port, topic) == (
                "mqtt.local",
                1883,
                "vigi/esteira/inspecoes",
            )

        def publish(self, event: InspectionEvent) -> None:
            published.append(event)

    monkeypatch.setattr(
        infer.InferenceEngine,
        "from_manifest",
        lambda _path: EngineStub(),
    )
    monkeypatch.setattr(
        infer,
        "MQTTInspectionPublisher",
        PublisherStub,
        raising=False,
    )

    exit_code = infer.main(
        [
            "--manifest",
            "models/active/manifest.json",
            "--image",
            str(image),
            "--mqtt-host",
            "mqtt.local",
        ]
    )

    assert exit_code == 0
    assert len(published) == 1
    assert published[0].inspection_id > 0
    assert published[0].nonconformity_type == "SEM_TAMPA"
