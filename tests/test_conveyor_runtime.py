"""
Descrição: Testa o ciclo de vida e o estado ocioso da esteira.
Autor: Leôncio Ferreira
"""

from unittest.mock import MagicMock

from edge.acquisition.sensor import SimulatedPhotoelectricSensor
from edge.messaging.publisher import MQTTInspectionPublisher
from edge.orchestration.conveyor import ConveyorOrchestrator
from tests.conveyor_fakes import CameraStub, InferenceEngineStub, inspection_decision


def test_conveyor_runs_and_stops_on_max_cycles() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=InferenceEngineStub(inspection_decision()),
        publisher=MQTTInspectionPublisher(client=MagicMock()),
    )
    sensor.trigger()
    sensor.trigger()

    orchestrator.run(max_cycles=2, poll_interval=0.01)

    assert orchestrator.inspections_count == 2
    assert camera.released


def test_conveyor_reports_idle_state_only_on_transitions() -> None:
    sensor = MagicMock()
    sensor.wait_for_trigger.side_effect = [False, False, True]
    idle_states: list[bool] = []
    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=CameraStub(),
        engine=InferenceEngineStub(inspection_decision()),
        publisher=MagicMock(),
        on_idle=idle_states.append,
    )

    orchestrator.run(max_cycles=1, poll_interval=0.01)

    assert idle_states == [True, False]
