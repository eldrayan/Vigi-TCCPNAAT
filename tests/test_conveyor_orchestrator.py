"""Testes do orquestrador ponta a ponta da esteira de inspeção."""

from typing import Any
from unittest.mock import MagicMock, patch

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

    def read(self) -> tuple[bool, Any]:
        self.read_count += 1
        dummy_frame = MagicMock()
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


def test_conveyor_applies_capture_delay_before_reading_camera() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    decision = InspectionDecision(
        result="CONFORME",
        category=None,
        nonconformity_type=None,
        technical_failure_type=None,
        confidence=0.98,
        processing_time_ms=45.0,
        model_format="pytorch",
    )
    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=InferenceEngineStub(decision),
        publisher=MagicMock(),
        capture_delay_s=0.18,
    )

    with patch("edge.orchestration.conveyor.time.sleep") as sleep:
        orchestrator.process_cycle()

    sleep.assert_called_once_with(0.18)


def test_conveyor_persists_and_delivers_through_outbox() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    decision = InspectionDecision(
        result="CONFORME",
        category=None,
        nonconformity_type=None,
        technical_failure_type=None,
        confidence=0.98,
        processing_time_ms=45.0,
        model_format="pytorch",
    )
    engine = InferenceEngineStub(decision)
    publisher = MagicMock()
    outbox = MagicMock()

    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=engine,
        publisher=publisher,
        outbox=outbox,
    )

    event, _ = orchestrator.process_cycle()

    outbox.enqueue.assert_called_once_with(event)
    outbox.deliver.assert_called_once_with(publisher)
    outbox.purge_expired.assert_called_once()
    publisher.publish_inspection.assert_not_called()


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


def test_conveyor_reports_idle_state_only_on_transitions() -> None:
    sensor = MagicMock()
    sensor.wait_for_trigger.side_effect = [False, False, True]
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
    idle_states: list[bool] = []

    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=InferenceEngineStub(decision),
        publisher=MagicMock(),
        on_idle=idle_states.append,
    )

    orchestrator.run(max_cycles=1, poll_interval=0.01)

    assert idle_states == [True, False]
