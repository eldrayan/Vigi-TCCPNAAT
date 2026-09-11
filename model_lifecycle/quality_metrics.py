"""Metricas do quality gate do classificador."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .inspection_classes import CLASS_NAMES, canonical_class


@dataclass(frozen=True)
class Prediction:
    expected: str
    predicted: str
    confidence: float
    path: str = ""


@dataclass(frozen=True)
class QualityMetrics:
    accuracy: float
    false_negative_rate: float
    false_positive_rate: float
    coverage: float
    sample_count: int
    confusion_matrix: list[list[int]]
    per_class_accuracy: dict[str, float]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def calculate_metrics(
    predictions: list[Prediction], confidence_threshold: float = 0.0
) -> QualityMetrics:
    if not predictions:
        raise ValueError("Nenhuma predicao fornecida")

    class_index = {name: index for index, name in enumerate(CLASS_NAMES)}
    confusion = [[0 for _ in CLASS_NAMES] for _ in CLASS_NAMES]
    correct = confident = false_negative = false_positive = 0
    conforming = defective = 0
    per_class_total = {name: 0 for name in CLASS_NAMES}
    per_class_correct = {name: 0 for name in CLASS_NAMES}

    for item in predictions:
        expected = canonical_class(item.expected)
        predicted = canonical_class(item.predicted)
        is_confident = item.confidence >= confidence_threshold
        per_class_total[expected] += 1
        confusion[class_index[expected]][class_index[predicted]] += 1
        if is_confident:
            confident += 1
        if is_confident and expected == predicted:
            correct += 1
            per_class_correct[expected] += 1

        expected_conforming = expected == "01_conforme"
        predicted_conforming = is_confident and predicted == "01_conforme"
        if expected_conforming:
            conforming += 1
            if not predicted_conforming:
                false_positive += 1
        else:
            defective += 1
            if predicted_conforming:
                false_negative += 1

    total = len(predictions)
    return QualityMetrics(
        accuracy=correct / total,
        false_negative_rate=false_negative / defective if defective else 0.0,
        false_positive_rate=false_positive / conforming if conforming else 0.0,
        coverage=confident / total,
        sample_count=total,
        confusion_matrix=confusion,
        per_class_accuracy={
            name: per_class_correct[name] / count if count else 0.0
            for name, count in per_class_total.items()
        },
    )


def choose_threshold(predictions: list[Prediction]) -> tuple[float, QualityMetrics]:
    """Escolhe o maior coverage que satisfaz FN/FP; desempata por acuracia."""
    candidates: list[tuple[float, QualityMetrics]] = []
    for step in range(0, 100):
        threshold = step / 100
        metrics = calculate_metrics(predictions, threshold)
        if metrics.false_negative_rate <= 0.10 and metrics.false_positive_rate <= 0.15:
            candidates.append((threshold, metrics))
    if not candidates:
        return 0.0, calculate_metrics(predictions, 0.0)
    return max(
        candidates, key=lambda item: (item[1].coverage, item[1].accuracy, item[0])
    )


def gate_passes(metrics: QualityMetrics) -> bool:
    return (
        metrics.accuracy >= 0.90
        and metrics.false_negative_rate <= 0.10
        and metrics.false_positive_rate <= 0.15
    )
