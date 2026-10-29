from dataclasses import dataclass
from typing import ClassVar

from journal.models.model import Model


@dataclass(frozen=True)
class DomainRow(Model):
    """A domain of the agentic organization as a row, by its id in the organization folder, so a task handed to one of its Roles can be linked to it; made when the first task is."""

    timeline_visible: ClassVar[bool] = False

    name: str = ""
