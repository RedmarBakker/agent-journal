from dataclasses import dataclass


@dataclass(frozen=True)
class TraceEntry:
    """One action of a simulated run: the simulated second it happened at, the actor, the action, whether the journal refused it, and the nudges said with it."""

    second: int
    actor: str
    action: str
    refused: bool
    nudges: tuple[str, ...]
