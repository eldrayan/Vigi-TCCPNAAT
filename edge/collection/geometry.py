"""Cálculos geométricos compartilhados entre coleta e apresentação."""


def guide_bounds(
    frame_width: int,
    frame_height: int,
    width_ratio: float,
    height_ratio: float,
) -> tuple[int, int, int, int]:
    guide_width = max(1, int(frame_width * width_ratio))
    guide_height = max(1, int(frame_height * height_ratio))
    x1 = max(0, (frame_width - guide_width) // 2)
    y1 = max(0, (frame_height - guide_height) // 2)
    return (
        x1,
        y1,
        min(frame_width, x1 + guide_width),
        min(frame_height, y1 + guide_height),
    )
