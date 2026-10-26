from dataclasses import dataclass


@dataclass(frozen=True)
class TraceEntry:
    """One action of a simulated run: the simulated second it happened at, the actor, the action, whether the journal refused it, the nudges said with it, the agent's stack after it, the status it was answered with, and the deferred work skipped so far."""

    second: int
    actor: str
    action: str
    refused: bool
    nudges: tuple[str, ...]
    stack: tuple[str, ...] = ()
    status: int = 0
    skipped: int = 0
