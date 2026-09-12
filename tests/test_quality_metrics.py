"""Testes das métricas do quality gate."""

from __future__ import annotations

from model_lifecycle.quality_metrics import (
    Prediction,
    calculate_metrics,
    choose_threshold,
    gate_passes,
)


def test_quality_metrics_for_perfect_predictions() -> None:
    predictions = [
        Prediction("01_conforme", "01_conforme", 0.95),
        Prediction("02_sem_tampa", "02_sem_tampa", 0.90),
        Prediction("03_tampa_torta", "03_tampa_torta", 0.92),
        Prediction("04_amassado", "04_amassado", 0.93),
    ]
    metrics = calculate_metrics(predictions, 0.80)
    assert metrics.accuracy == 1.0
    assert metrics.false_negative_rate == 0.0
    assert metrics.false_positive_rate == 0.0
    assert gate_passes(metrics)


def test_low_confidence_conforming_is_a_preventive_false_positive() -> None:
    predictions = [
        Prediction("01_conforme", "01_conforme", 0.40),
        Prediction("02_sem_tampa", "02_sem_tampa", 0.95),
    ]
    metrics = calculate_metrics(predictions, 0.70)
    assert metrics.coverage == 0.5
    assert metrics.false_positive_rate == 1.0
    assert metrics.false_negative_rate == 0.0


def test_choose_threshold_uses_validation_predictions() -> None:
    predictions = [
        Prediction("01_conforme", "01_conforme", 0.90),
        Prediction("02_sem_tampa", "02_sem_tampa", 0.80),
    ]
    threshold, metrics = choose_threshold(predictions)
    assert threshold <= 0.80
    assert metrics.coverage == 1.0
