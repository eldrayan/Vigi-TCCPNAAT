from __future__ import annotations

from edge.inference.schemas import InspectionDecision
from scripts.benchmark_modelo import build_report, main


def decision(
    latency: float,
    code: str | None = None,
    category: str | None = None,
) -> InspectionDecision:
    return InspectionDecision(
        resultado="CONFORME" if code is None else "NAO_CONFORME",
        categoria=category,
        codigo=code,
        confianca=None if code == "ERRO_INFERENCIA" else 0.9,
        tempo_processamento_ms=latency,
        formato_modelo="pytorch",
    )


def report(
    measured: list[InspectionDecision],
    warmup: list[InspectionDecision] | None = None,
) -> dict[str, object]:
    return build_report(
        "pytorch",
        len(measured),
        len(warmup or []),
        warmup or [],
        measured,
    )


def test_gate_accepts_exactly_95_percent_within_500ms() -> None:
    payload = report([decision(500)] * 95 + [decision(600)] * 5)

    assert payload["within_500ms_ratio"] == 0.95
    assert payload["latency_gate"] is True


def test_gate_rejects_94_percent_within_500ms() -> None:
    payload = report([decision(500)] * 94 + [decision(600)] * 6)

    assert payload["within_500ms_ratio"] == 0.94
    assert payload["latency_gate"] is False


def test_gate_includes_exact_500ms_and_1000ms_limits() -> None:
    payload = report([decision(500)] * 95 + [decision(1000)] * 5)

    assert payload["max_ms"] == 1000
    assert payload["latency_gate"] is True


def test_gate_rejects_latency_above_1000ms() -> None:
    payload = report([decision(100)] * 99 + [decision(1000.01)])

    assert payload["latency_gate"] is False


def test_measurement_error_fails_and_is_excluded_from_statistics() -> None:
    measured = [decision(100)] * 99 + [decision(5000, "ERRO_INFERENCIA")]
    payload = report(measured)

    assert payload["successful_runs"] == 99
    assert payload["inference_errors"] == 1
    assert payload["within_500ms_ratio"] == 0.99
    assert payload["max_ms"] == 100
    assert payload["latency_gate"] is False


def test_all_measurements_failing_produces_null_statistics() -> None:
    payload = report([decision(5000, "ERRO_INFERENCIA")] * 3)

    assert payload["successful_runs"] == 0
    assert payload["inference_errors"] == 3
    assert payload["within_500ms_ratio"] == 0
    assert payload["mean_ms"] is None
    assert payload["p50_ms"] is None
    assert payload["p95_ms"] is None
    assert payload["max_ms"] is None
    assert payload["latency_gate"] is False


def test_warmup_error_fails_without_affecting_measured_statistics() -> None:
    payload = report(
        [decision(100)] * 100,
        [decision(9000, "ERRO_INFERENCIA")],
    )

    assert payload["warmup_errors"] == 1
    assert payload["mean_ms"] == 100
    assert payload["latency_gate"] is False


def test_low_confidence_and_product_anomaly_are_successful_runs() -> None:
    payload = report(
        [
            decision(100, "BAIXA_CONFIANCA", "FALHA_TECNICA"),
            decision(100, "SEM_TAMPA", "ANOMALIA_PRODUTO"),
        ]
    )

    assert payload["successful_runs"] == 2
    assert payload["inference_errors"] == 0
    assert payload["latency_gate"] is True


def test_main_runs_every_warmup_and_measurement(monkeypatch, tmp_path) -> None:
    image = tmp_path / "sample.jpg"
    image.write_bytes(b"image content is not decoded by the benchmark")

    class Manifest:
        format = "pytorch"

    class Engine:
        manifest = Manifest()

        def __init__(self) -> None:
            self.calls = 0

        def inspect(self, _image: str) -> InspectionDecision:
            self.calls += 1
            return decision(10, "ERRO_INFERENCIA")

    engine = Engine()
    monkeypatch.setattr(
        "scripts.benchmark_modelo.InferenceEngine.from_manifest",
        lambda _path: engine,
    )

    exit_code = main(
        [
            "--manifest",
            str(tmp_path / "manifest.json"),
            "--images",
            str(tmp_path),
            "--warmup",
            "2",
            "--runs",
            "3",
        ]
    )

    assert engine.calls == 5
    assert exit_code == 1
