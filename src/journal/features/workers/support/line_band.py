from dataclasses import dataclass

from journal.features.workers.support.handout_direction import HandoutDirection
from journal.models.support.pressure_band import PressureBand


@dataclass(frozen=True)
class LineBand:
    """Where one measure line of a mode speaks: the bands it may speak in and which way it pushes the agent."""

    mode: str
    nudge_key: str
    bands: tuple[PressureBand, ...]
    direction: HandoutDirection
