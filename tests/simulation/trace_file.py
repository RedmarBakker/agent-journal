import json
from dataclasses import asdict
from pathlib import Path

from tests.simulation.trace_entry import TraceEntry


class TraceFile:
    """A failing run written where it can be replayed: its scenario, its seed, the invariant it broke and its agent's actions, as JSON."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def written(self, scenario: str, seed: int, broken: str, trace: list[TraceEntry], actions: list[str]) -> Path:
        self.folder.mkdir(parents=True, exist_ok=True)
        path = self.folder / f"{scenario.replace(' ', '_')}-{seed}.json"
        path.write_text(json.dumps({"scenario": scenario, "seed": seed, "broken": broken, "actions": actions, "trace": [asdict(entry) for entry in trace]}, indent=2) + "\n")
        return path
