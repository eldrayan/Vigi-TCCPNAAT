"""Testes do orquestrador ponta a ponta da esteira de inspeção."""

from typing import Any
from unittest.mock import MagicMock

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


class IndicatorsStub:
    def __init__(self) -> None:
        self.results: list[str] = []
        self.critical_alarm_count = 0
        self.acknowledged_count = 0
        self.closed = False

    def signal_result(self, result: str) -> None:
        self.results.append(result)

    def signal_critical_alarm(self) -> None:
        self.critical_alarm_count += 1

    def acknowledge_alarm(self) -> None:
        self.acknowledged_count += 1

    def close(self) -> None:
        self.closed = True


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


def test_conveyor_signals_each_result_and_alarms_after_consecutive_rejections() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    decision = InspectionDecision(
        result="NAO_CONFORME",
        category="ANOMALIA_PRODUTO",
        nonconformity_type="SEM_TAMPA",
        technical_failure_type=None,
        confidence=0.95,
        processing_time_ms=40.0,
        model_format="pytorch",
    )
    indicators = IndicatorsStub()
    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=InferenceEngineStub(decision),
        publisher=MQTTInspectionPublisher(client=MagicMock()),
        indicators=indicators,
        critical_alarm_after=2,
    )

    orchestrator.process_cycle()
    assert indicators.results == ["NAO_CONFORME"]
    assert indicators.critical_alarm_count == 0

    orchestrator.process_cycle()
    assert indicators.results == ["NAO_CONFORME", "NAO_CONFORME"]
    assert indicators.critical_alarm_count == 1

    orchestrator.acknowledge_alarm()
    assert indicators.acknowledged_count == 1

    orchestrator.process_cycle()
    assert indicators.critical_alarm_count == 1

    orchestrator.process_cycle()
    assert indicators.critical_alarm_count == 2


def test_conveyor_resets_rejection_streak_after_conforming_result() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    engine = InferenceEngineStub(
        InspectionDecision(
            result="NAO_CONFORME",
            category="ANOMALIA_PRODUTO",
            nonconformity_type="TAMPA_TORTA",
            technical_failure_type=None,
            confidence=0.9,
            processing_time_ms=40.0,
            model_format="pytorch",
        )
    )
    indicators = IndicatorsStub()
    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=engine,
        publisher=MQTTInspectionPublisher(client=MagicMock()),
        indicators=indicators,
        critical_alarm_after=2,
    )

    orchestrator.process_cycle()
    engine.decision = InspectionDecision(
        result="CONFORME",
        category=None,
        nonconformity_type=None,
        technical_failure_type=None,
        confidence=0.99,
        processing_time_ms=35.0,
        model_format="pytorch",
    )
    orchestrator.process_cycle()
    engine.decision = InspectionDecision(
        result="NAO_CONFORME",
        category="ANOMALIA_PRODUTO",
        nonconformity_type="AMASSADO",
        technical_failure_type=None,
        confidence=0.91,
        processing_time_ms=42.0,
        model_format="pytorch",
    )
    orchestrator.process_cycle()

    assert indicators.results == ["NAO_CONFORME", "CONFORME", "NAO_CONFORME"]
    assert indicators.critical_alarm_count == 0


def test_conveyor_closes_indicators_with_other_hardware() -> None:
    sensor = SimulatedPhotoelectricSensor()
    camera = CameraStub()
    indicators = IndicatorsStub()
    decision = InspectionDecision(
        result="CONFORME",
        category=None,
        nonconformity_type=None,
        technical_failure_type=None,
        confidence=0.99,
        processing_time_ms=30.0,
        model_format="pytorch",
    )
    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=InferenceEngineStub(decision),
        publisher=MQTTInspectionPublisher(client=MagicMock()),
        indicators=indicators,
    )

    orchestrator.stop()

    assert indicators.closed


def test_conveyor_triggers_immediate_alarm_for_technical_failure() -> None:
    indicators = IndicatorsStub()
    decision = InspectionDecision(
        result="NAO_CONFORME",
        category="FALHA_TECNICA",
        nonconformity_type=None,
        technical_failure_type="ERRO_INFERENCIA",
        confidence=None,
        processing_time_ms=5.0,
        model_format="pytorch",
    )
    orchestrator = ConveyorOrchestrator(
        sensor=SimulatedPhotoelectricSensor(),
        camera=CameraStub(),
        engine=InferenceEngineStub(decision),
        publisher=MQTTInspectionPublisher(client=MagicMock()),
        indicators=indicators,
        critical_alarm_after=3,
    )

    orchestrator.process_cycle()

    assert indicators.critical_alarm_count == 1


def test_led_failure_does_not_suppress_critical_buzzer() -> None:
    indicators = IndicatorsStub()

    def fail_to_signal_result(result: str) -> None:
        raise RuntimeError("LED indisponível")

    indicators.signal_result = fail_to_signal_result
    decision = InspectionDecision(
        result="NAO_CONFORME",
        category="FALHA_TECNICA",
        nonconformity_type=None,
        technical_failure_type="ERRO_INFERENCIA",
        confidence=None,
        processing_time_ms=5.0,
        model_format="pytorch",
    )
    orchestrator = ConveyorOrchestrator(
        sensor=SimulatedPhotoelectricSensor(),
        camera=CameraStub(),
        engine=InferenceEngineStub(decision),
        publisher=MQTTInspectionPublisher(client=MagicMock()),
        indicators=indicators,
    )

    orchestrator.process_cycle()

    assert indicators.critical_alarm_count == 1


def test_external_critical_rule_can_trigger_physical_alarm() -> None:
    indicators = IndicatorsStub()
    decision = InspectionDecision(
        result="CONFORME",
        category=None,
        nonconformity_type=None,
        technical_failure_type=None,
        confidence=0.99,
        processing_time_ms=30.0,
        model_format="pytorch",
    )
    orchestrator = ConveyorOrchestrator(
        sensor=SimulatedPhotoelectricSensor(),
        camera=CameraStub(),
        engine=InferenceEngineStub(decision),
        publisher=MQTTInspectionPublisher(client=MagicMock()),
        indicators=indicators,
    )

    orchestrator.trigger_critical_alarm()

    assert indicators.critical_alarm_count == 1
