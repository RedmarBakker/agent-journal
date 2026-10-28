import json
from datetime import datetime
from pathlib import Path

from journal.config import Config
from journal.models.state_transition import StateTransition
from journal.repositories.state_transitions import StateTransitions
from journal.support.time_source import TimeSource

FILE_NAME = "scenario-transitions.json"
HOUR_SECONDS = 3600


class ScenarioTransitions:
    """The kinds of stack change counted here, rarest first, each set against the kinds the last full scenario run walked, which that run writes to the journal's runtime folder."""

    def __init__(self, config: Config, transitions: StateTransitions, time_source: TimeSource) -> None:
        self.walked_file, self.transitions, self.time_source = ScenarioTransitions.walked_path(config), transitions, time_source

    @staticmethod
    def walked_path(config: Config) -> Path:
        return config.home / "runtime" / FILE_NAME

    def lines(self, hours: float) -> list[str]:
        earliest = self.time_source.seconds() - hours * HOUR_SECONDS if hours else 0.0
        walked = self.walked()
        return [self.line(row, walked) for row in self.transitions.seen_since(earliest)]

    def walked(self) -> set[str]:
        return set(json.loads(self.walked_file.read_text())) if self.walked_file.exists() else set()

    def footer(self) -> str:
        return f"marked: no story walks it, from {self.walked_file}" if self.walked_file.exists() else f"no full scenario run has written {self.walked_file}, so nothing is marked"

    def line(self, row: StateTransition, walked: set[str]) -> str:
        mark = "  no story walks it" if walked and row.kind() not in walked else ""
        return f"{row.count:>7}  {row.kind()}  last {datetime.fromtimestamp(row.last_at):%Y-%m-%d %H:%M}{mark}"
