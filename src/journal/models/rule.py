from dataclasses import dataclass, field
from typing import ClassVar

from journal.events.rows.rule_created import RuleCreated
from journal.models.model import Model
from journal.models.support.commentable import Commentable


@dataclass(frozen=True)
class Rule(Model, Commentable):
    """Project-wide: binds every environment."""

    text_fields: ClassVar[tuple[str, ...]] = ("text", "reason")

    text: str = ""
    reason: str = ""
    keywords: tuple[str, ...] = ()
    trigger: str = ""
    condition: dict = field(default_factory=dict)
    is_single_use: bool = False
    presence: bool = False

    def created(self, agent_index: bool) -> "Rule":
        return self.with_event(RuleCreated(agent_origin=agent_index))

    def summary_line(self) -> str:
        return self.opening_line(self.text)
