"""Representa uma estação retornada pela API."""

from datetime import datetime

from pydantic import ConfigDict

from .station_create import StationCreateDTO


class StationResponseDTO(StationCreateDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
