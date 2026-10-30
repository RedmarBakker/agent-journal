from dataclasses import dataclass, field

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class ForecastSnapshot(Scoped):
    """One immutable delivery forecast and the input cut that produced it."""

    snapshot_key: str = ""
    input_cut: str = ""
    captured_at: float = 0.0
    seed: int = 0
    method_version: str = ""
    data: dict = field(default_factory=dict)
