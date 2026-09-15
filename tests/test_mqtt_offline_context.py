"""Regressoes do uso de contexto operacional quando o broker esta offline."""

from edge.inference.schemas import InspectionDecision
from edge.messaging import InspectionEvent, OperationalContext
from scripts import infer


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


def test_inference_cli_uses_cached_context_when_broker_is_offline(
    monkeypatch, tmp_path
) -> None:
    image = tmp_path / "sample.jpg"
    image.write_bytes(b"imagem simulada")
    published: list[InspectionEvent] = []

    class EngineStub:
        def inspect(self, source: str) -> InspectionDecision:
            return decision()

    class PublisherStub:
        def __init__(self, **kwargs) -> None:
            return None

        def publish(self, event: InspectionEvent, topic: str | None = None) -> None:
            published.append(event)

    class OutboxStub:
        def __init__(self, path) -> None:
            return None

        def load_context(self) -> OperationalContext:
            return OperationalContext("envase-01", "LOTE-001")

        def enqueue(self, event: InspectionEvent) -> None:
            self.event = event

        def deliver(self, publisher: PublisherStub) -> int:
            publisher.publish(self.event, topic=self.event.inspections_topic)
            return 1

        def purge_expired(self, **kwargs) -> int:
            return 0

    monkeypatch.setattr(
        infer.InferenceEngine, "from_manifest", lambda _path: EngineStub()
    )
    monkeypatch.setattr(
        infer,
        "load_operational_context",
        lambda *args: (_ for _ in ()).throw(ConnectionError("sem broker")),
    )
    monkeypatch.setattr(infer, "InspectionOutbox", OutboxStub)
    monkeypatch.setattr(infer, "MQTTInspectionPublisher", PublisherStub)

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
    assert published[0].station_code == "envase-01"
