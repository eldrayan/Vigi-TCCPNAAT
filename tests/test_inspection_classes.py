"""Testes do catálogo de classes de inspeção."""

from __future__ import annotations

import pytest

from model_lifecycle.inspection_classes import canonical_class


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("01_conforme", "01_conforme"),
        ("conforme", "01_conforme"),
        ("SEM TAMPA", "02_sem_tampa"),
        ("tampa-torta", "03_tampa_torta"),
        ("AMASSADO", "04_amassado"),
    ],
)
def test_canonical_class_accepts_domain_aliases(value: str, expected: str) -> None:
    assert canonical_class(value) == expected


def test_canonical_class_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="Classe desconhecida"):
        canonical_class("vazia")
