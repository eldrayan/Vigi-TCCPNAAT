"""
Descrição: Testa o processamento unitário dos ciclos da esteira.
Autor: Leôncio Ferreira
"""

from unittest.mock import MagicMock, patch

from edge.acquisition.sensor import SimulatedPhotoelectricSensor
from edge.messaging.event import InspectionEvent
from edge.messaging.publisher import MQTTInspectionPublisher
from edge.orchestration.conveyor import ConveyorOrchestrator, CycleTiming
from tests.conveyor_fakes import CameraStub, InferenceEngineStub, inspection_decision


def test_conveyor_process_cycle_conforme() -> None:
    camera = CameraStub()
    mock_client = MagicMock()
    callback_calls: list[tuple[InspectionEvent, CycleTiming]] = []
    orchestrator = ConveyorOrchestrator(
        sensor=SimulatedPhotoelectricSensor(),
        camera=camera,
        engine=InferenceEngineStub(inspection_decision()),
        publisher=MQTTInspectionPublisher(client=mock_client),
        on_inspection=lambda event, timing: callback_calls.append((event, timing)),
    )

    event, timing = orchestrator.process_cycle()

    assert event.result == "CONFORME"
    assert orchestrator.inspections_count == 1
    assert len(callback_calls) == 1
    assert 0 < timing.total_ms < 500.0
    assert mock_client.publish.call_args[0][0] == "vigi/esteira/inspecoes"


def test_conveyor_applies_capture_delay_before_reading_camera() -> None:
    orchestrator = ConveyorOrchestrator(
        sensor=SimulatedPhotoelectricSensor(),
        camera=CameraStub(),
        engine=InferenceEngineStub(inspection_decision()),
        publisher=MagicMock(),
        capture_delay_s=0.18,
    )

    with patch("edge.orchestration.conveyor.time.sleep") as sleep:
        orchestrator.process_cycle()

    sleep.assert_called_once_with(0.18)


def test_conveyor_persists_and_delivers_through_outbox() -> None:
    publisher = MagicMock()
    outbox = MagicMock()
    orchestrator = ConveyorOrchestrator(
        sensor=SimulatedPhotoelectricSensor(),
        camera=CameraStub(),
        engine=InferenceEngineStub(inspection_decision()),
        publisher=publisher,
        outbox=outbox,
    )

    event, _ = orchestrator.process_cycle()

    outbox.enqueue.assert_called_once_with(event)
    outbox.deliver.assert_called_once_with(publisher)
    outbox.purge_expired.assert_called_once()
    publisher.publish_inspection.assert_not_called()


def test_conveyor_process_cycle_nonconformity_triggers_alarm() -> None:
    mock_client = MagicMock()
    orchestrator = ConveyorOrchestrator(
        sensor=SimulatedPhotoelectricSensor(),
        camera=CameraStub(),
        engine=InferenceEngineStub(
            inspection_decision("NAO_CONFORME", "TAMPA_TORTA")
        ),
        publisher=MQTTInspectionPublisher(client=mock_client),
    )

    event, _ = orchestrator.process_cycle()

    assert event.result == "NAO_CONFORME"
    assert event.nonconformity_type == "TAMPA_TORTA"
    topics = [call[0][0] for call in mock_client.publish.call_args_list]
    assert topics == ["vigi/esteira/inspecoes", "vigi/esteira/alarmes"]
