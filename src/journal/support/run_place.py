from dataclasses import dataclass


@dataclass(frozen=True)
class RunPlace:
    """Where a chat card stands in a run of cards: which run, its step in it, and the run's title, so the viewer gathers a run's cards in step order."""

    run: str
    step: int
    run_title: str
