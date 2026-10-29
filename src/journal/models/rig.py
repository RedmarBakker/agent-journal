from dataclasses import dataclass
from typing import ClassVar

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class Rig(Scoped):
    """An OpenRig rig run in this environment, by its name there: an organization plan's, linked from the plan, or the one shared by every plan's journal-cardinality Roles. Stored on this machine."""

    shared: ClassVar[bool] = False
    timeline_visible: ClassVar[bool] = False

    name: str = ""
