from typing import ClassVar
from dataclasses import dataclass

from journal.models.model import Model
from journal.models.trigger_action import TriggerAction
from journal.support.phrases import Phrases


@dataclass(frozen=True)
class Trigger(Model):
    """Words the user chose, and what the journal does when one comes up in a prompt or a tool call."""

    text_fields: ClassVar[tuple[str, ...]] = ("phrases",)
    phrases: tuple[str, ...] = ()
    action: TriggerAction = TriggerAction.NUDGE
    text: str = ""

    def matches(self, text: str) -> bool:
        return any(Phrases.contains(text, phrase) for phrase in self.phrases)

    def summary_line(self) -> str:
        return self.opening_line(self.text)
