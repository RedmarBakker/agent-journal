from dataclasses import dataclass

from journal.support.actor import Actor
from journal.support.response import Response
from journal.supervisor_principal import SupervisorPrincipal


@dataclass(frozen=True)
class SupervisorAccess:
    actor: Actor | None = None
    principal: SupervisorPrincipal | None = None
    error: Response | None = None
