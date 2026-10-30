from dataclasses import dataclass
from typing import ClassVar

from journal.models.model import Model
from journal.models.support.ref import Ref


@dataclass(frozen=True, kw_only=True)
class Link(Model):
    """A relation between any two rows. Models declare no relations themselves; every one is a row here, with a kind that says what it means. A deleted row takes its links with it."""

    column_renames: ClassVar[dict[str, str]] = {"kind": "link_type"}


    source: Ref
    target: Ref
    link_type: str
