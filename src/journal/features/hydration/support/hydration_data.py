from dataclasses import dataclass


@dataclass(frozen=True)
class HydrationData:
    """The hydration feature's reading: the agent program and session the environment's chat was filled from, while its agent has not yet been asked to read it; empty otherwise."""

    provider: str = ""
    session: str = ""
