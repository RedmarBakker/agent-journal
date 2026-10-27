from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from journal.events.data_source import DataSource
from journal.models.open_task import OpenTask

# the field a feature's part offers the work of that feature the agent could take up now under, or none
OPEN_WORK = "open_work"


@dataclass(frozen=True)
class FeatureData:
    """What the features read about the environment's rows for the agent the state machine asks, one frozen part per feature, read by the feature and typed by the data class the feature names."""

    parts: Mapping[str, Any]

    def part[D](self, source: type[DataSource[D]]) -> D:
        return self.parts[source.name] if source.name in self.parts else source.missing()

    def next_work(self) -> OpenTask | None:
        offers = (getattr(part, OPEN_WORK, None) for part in self.parts.values())
        return next((work for work in offers if work is not None), None)

    def has_open_work(self) -> bool:
        return self.next_work() is not None
