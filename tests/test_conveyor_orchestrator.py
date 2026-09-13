"""Testes do orquestrador ponta a ponta da esteira de inspeção."""

from unittest.mock import MagicMock

import numpy as np

from edge.acquisition.sensor import SimulatedPhotoelectricSensor
from edge.inference.schemas import InspectionDecision
from edge.messaging.event import InspectionEvent
from edge.messaging.publisher import MQTTInspectionPublisher
from edge.orchestration.conveyor import ConveyorOrchestrator, CycleTiming


class CameraStub:
    def __init__(self) -> None:
        self.read_count = 0
        self.released = False

    def is_opened(self) -> bool:
        return not self.released

    def read(self) -> tuple[bool, np.ndarray]:
        self.read_count += 1
        dummy_frame = np.zeros((224, 224, 3), dtype=np.uint8)
        return True, dummy_frame

    def release(self) -> None:
        self.released = True


class InferenceEngineStub:
    def __init__(self, decision: InspectionDecision) -> None:
        self.decision = decision
        self.inspect_called = 0

    def inspect(self, frame) -> InspectionDecision:
        self.inspect_called += 1
        return self.decision


def test_conveyor_process_cycle_conforme() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    conforme_decision = InspectionDecision(
        result="CONFORME",
        category=None,
        nonconformity_type=None,
        technical_failure_type=None,
        confidence=0.98,
        processing_time_ms=45.0,
        model_format="pytorch",
    )
    engine = InferenceEngineStub(conforme_decision)

    mock_client = MagicMock()
    publisher = MQTTInspectionPublisher(client=mock_client)

    callback_calls = []

    def on_inspection(event: InspectionEvent, timing: CycleTiming) -> None:
        callback_calls.append((event, timing))

    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=engine,
        publisher=publisher,
        on_inspection=on_inspection,
    )

    event, timing = orchestrator.process_cycle()

    assert event.result == "CONFORME"
    assert orchestrator.inspections_count == 1
    assert len(callback_calls) == 1
    assert timing.total_ms > 0
    # Valida RNF01 (< 500 ms)
    assert timing.total_ms < 500.0

    # Publicou no tópico de inspeções
    assert mock_client.publish.call_count == 1
    call_topic = mock_client.publish.call_args[0][0]
    assert call_topic == "vigi/esteira/inspecoes"


def test_conveyor_process_cycle_nonconformity_triggers_alarm() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    defect_decision = InspectionDecision(
        result="NAO_CONFORME",
        category="ANOMALIA_PRODUTO",
        nonconformity_type="TAMPA_TORTA",
        technical_failure_type=None,
        confidence=0.92,
        processing_time_ms=50.0,
        model_format="pytorch",
    )
    engine = InferenceEngineStub(defect_decision)

    mock_client = MagicMock()
    publisher = MQTTInspectionPublisher(client=mock_client)

    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=engine,
        publisher=publisher,
    )

    event, _ = orchestrator.process_cycle()

    assert event.result == "NAO_CONFORME"
    assert event.nonconformity_type == "TAMPA_TORTA"

    # Deve ter publicado 2 mensagens: 1 de inspeção e 1 de alarme operacional
    assert mock_client.publish.call_count == 2
    topics = [call[0][0] for call in mock_client.publish.call_args_list]
    assert "vigi/esteira/inspecoes" in topics
    assert "vigi/esteira/alarmes" in topics


def test_conveyor_runs_and_stops_on_max_cycles() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    decision = InspectionDecision(
        result="CONFORME",
        category=None,
        nonconformity_type=None,
        technical_failure_type=None,
        confidence=0.99,
        processing_time_ms=30.0,
        model_format="pytorch",
    )
    engine = InferenceEngineStub(decision)
    mock_client = MagicMock()
    publisher = MQTTInspectionPublisher(client=mock_client)

    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=engine,
        publisher=publisher,
    )

    # Dispara o sensor 2 vezes
    sensor.trigger()
    sensor.trigger()

    orchestrator.run(max_cycles=2, poll_interval=0.01)

    assert orchestrator.inspections_count == 2
    assert camera.released
