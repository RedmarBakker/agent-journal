from dataclasses import dataclass
from typing import Any

from journal.support.actor import Actor


@dataclass(frozen=True)
class SupervisorPrincipal:
    grant_id: str
    grant_version: int
    owner_user_id: int
    scope: dict[str, Any]
    actor: Actor
