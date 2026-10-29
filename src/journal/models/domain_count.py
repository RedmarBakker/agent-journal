from dataclasses import dataclass, field
from typing import ClassVar

from journal.models.model import Model


@dataclass(frozen=True)
class DomainCount(Model):
    """The live figures of one domain, kept as a row so the viewer reads them without a query per Role: the plans active now, and for each Role of the domain its running instances and the tasks queued for them. Kept on this machine, since the instances are its own."""

    shared: ClassVar[bool] = False

    name: str = ""
    plans_active: int = 0
    roles: dict = field(default_factory=dict)
