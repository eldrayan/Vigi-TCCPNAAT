"""
Descrição: Fornece objetos auxiliares para os testes da esteira.
Autor: Leôncio Ferreira
"""

from typing import Any
from unittest.mock import MagicMock

from edge.inference.schemas import InspectionDecision


class CameraStub:
    def __init__(self) -> None:
        self.read_count = 0
        self.released = False

    def is_opened(self) -> bool:
        return not self.released

    def read(self) -> tuple[bool, Any]:
        self.read_count += 1
        return True, MagicMock()

    def release(self) -> None:
        self.released = True


class InferenceEngineStub:
    def __init__(self, decision: InspectionDecision) -> None:
        self.decision = decision
        self.inspect_called = 0

    def inspect(self, frame: Any) -> InspectionDecision:
        self.inspect_called += 1
        return self.decision


def inspection_decision(
    result: str = "CONFORME",
    nonconformity_type: str | None = None,
) -> InspectionDecision:
    return InspectionDecision(
        result=result,
        category="ANOMALIA_PRODUTO" if nonconformity_type else None,
        nonconformity_type=nonconformity_type,
        technical_failure_type=None,
        confidence=0.98,
        processing_time_ms=45.0,
        model_format="pytorch",
    )
