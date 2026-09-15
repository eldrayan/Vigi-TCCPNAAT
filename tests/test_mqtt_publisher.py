"""Testes da composição e publicação de eventos de inspeção no MQTT."""

from datetime import UTC, datetime

from edge.inference.schemas import InspectionDecision
from edge.messaging import (
    InspectionEvent,
    MQTTInspectionPublisher,
    MQTTOperationalContextReceiver,
    OperationalContext,
)
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


def test_context_defines_topics_for_device_and_station() -> None:
    context = OperationalContext("envase-01", "LOTE-001")

    assert context.inspections_topic == "vigi/estacoes/envase-01/inspecoes"


def test_receiver_reads_retained_operational_context() -> None:
    class ContextClientStub:
        def connect(self, host: str, port: int) -> None:
            self.connected_to = (host, port)

        def subscribe(self, topic: str, qos: int) -> None:
            self.subscribed_to = (topic, qos)

        def loop_start(self) -> None:
            message = type(
                "Message",
                (),
                {"payload": (b'{"station_code":"envase-01","batch_code":"LOTE-001"}')},
            )()
            self.on_message(self, None, message)

        def disconnect(self) -> None:
            self.disconnected = True

        def loop_stop(self) -> None:
            self.loop_stopped = True

    client = ContextClientStub()
    context = MQTTOperationalContextReceiver(
        host="mqtt.local",
        port=1883,
        device_id="leocio-raspberry",
        client=client,
    ).receive()

    assert client.connected_to == ("mqtt.local", 1883)
    assert client.subscribed_to == (
        "vigi/dispositivos/leocio-raspberry/configuracao",
        1,
    )
    assert context == OperationalContext("envase-01", "LOTE-001")
    assert client.disconnected
    assert client.loop_stopped


def test_event_adds_identifier_and_timestamp_to_decision() -> None:
    timestamp = datetime(2026, 9, 11, 15, 0, tzinfo=UTC)

    event = InspectionEvent.from_decision(
        decision(),
        context=OperationalContext("envase-01", "LOTE-001"),
        timestamp=timestamp,
        inspection_id=123,
    )

    assert event.as_dict() == {
        "inspection_id": 123,
        "timestamp": "2026-09-11T15:00:00+00:00",
        "station_code": "envase-01",
        "batch_code": "LOTE-001",
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
        context=OperationalContext("envase-01", "LOTE-001"),
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
                "vigi/estacoes/envase-01/inspecoes",
            )

        def publish(self, event: InspectionEvent, topic: str | None = None) -> None:
            assert topic == "vigi/estacoes/envase-01/inspecoes"
            published.append(event)

    class OutboxStub:
        def __init__(self, path) -> None:
            self.path = path
            self.events: list[InspectionEvent] = []

        def enqueue(self, event: InspectionEvent) -> None:
            self.events.append(event)

        def save_context(self, context: OperationalContext) -> None:
            self.context = context

        def deliver(self, publisher: PublisherStub) -> int:
            for event in self.events:
                publisher.publish(event, topic=event.inspections_topic)
            return len(self.events)

        def purge_expired(self, **kwargs) -> int:
            return 0

    monkeypatch.setattr(
        infer.InferenceEngine,
        "from_manifest",
        lambda _path: EngineStub(),
    )
    monkeypatch.setattr(
        infer,
        "load_operational_context",
        lambda host, port, device_id: OperationalContext(
            station_code="envase-01", batch_code="LOTE-001"
        ),
    )
    monkeypatch.setattr(
        infer,
        "MQTTInspectionPublisher",
        PublisherStub,
        raising=False,
    )
    monkeypatch.setattr(infer, "InspectionOutbox", OutboxStub, raising=False)

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
    assert published[0].station_code == "envase-01"
    assert published[0].batch_code == "LOTE-001"
    assert published[0].nonconformity_type == "SEM_TAMPA"
