"""Modelo de estado da sessão de coleta."""

from __future__ import annotations

from dataclasses import dataclass, field

CLASSES = {
    1: "01_conforme",
    2: "02_sem_tampa",
    3: "03_tampa_torta",
    4: "04_amassado",
}


def class_from_key(key: int) -> int | None:
    if ord("1") <= key <= ord("4"):
        return key - ord("0")
    return None


def safe_component(value: str) -> str:
    cleaned = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_" for char in value
    ).strip("_")
    return cleaned or "sessao"


@dataclass
class CaptureState:
    session_id: str
    selected_class: int = 1
    burst_enabled: bool = False
    crop_guide: bool = False
    physical_samples: dict[int, int] = field(
        default_factory=lambda: {class_id: 1 for class_id in CLASSES}
    )
    saved_by_class: dict[int, int] = field(
        default_factory=lambda: {class_id: 0 for class_id in CLASSES}
    )
    rejected_blurry: int = 0

    def __post_init__(self) -> None:
        self.session_id = safe_component(self.session_id)

    @property
    def class_name(self) -> str:
        return CLASSES[self.selected_class]

    @property
    def physical_sample(self) -> int:
        return self.physical_samples[self.selected_class]

    @property
    def group_id(self) -> str:
        return (
            f"{self.session_id}__{self.class_name}__frasco_{self.physical_sample:03d}"
        )

    def select_class(self, class_id: int) -> None:
        if class_id not in CLASSES:
            raise ValueError(f"Classe inválida: {class_id}")
        self.selected_class = class_id
        self.burst_enabled = False

    def next_physical_sample(self) -> None:
        self.physical_samples[self.selected_class] += 1
        self.burst_enabled = False
