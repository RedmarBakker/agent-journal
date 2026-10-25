from dataclasses import dataclass
from typing import ClassVar

from journal.models.model import Model
from journal.models.support.ref import Ref


@dataclass(frozen=True, kw_only=True)
class Link(Model):
    """A relation between any two rows. Models declare no relations themselves; every one is a row here, with a kind that says what it means. A deleted row takes its links with it, but for a copy's link to the row it was copied from and an attachment's link from the document attached, which stay to show their source removed."""

    COPIED_FROM: ClassVar[str] = "copied_from"
    ATTACHED_TO: ClassVar[str] = "attached_to"
    SURVIVING_SOURCE: ClassVar[tuple[str, ...]] = (ATTACHED_TO,)
    SURVIVING_TARGET: ClassVar[tuple[str, ...]] = (COPIED_FROM,)

    source: Ref
    target: Ref
    kind: str
