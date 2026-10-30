from dataclasses import dataclass

from journal.support.actor import Actor
from journal.support.agent_token import AgentToken


@dataclass(frozen=True)
class SeatWorker:
    """The journal worker a seat boots as: its actor, the token that proves it and the environment it works in."""

    actor: Actor
    token: AgentToken
    environment: str
    organization_seat: str = ""
    organization_rig: str = ""
