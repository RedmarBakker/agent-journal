from typing import ClassVar
from dataclasses import dataclass

from journal.models.model import Model
from journal.models.support.sequence_step import SequenceStep
from journal.models.support.sequence_trigger import SequenceTrigger
from journal.models.support.sequence_trigger_type import SequenceTriggerType
from journal.support.phrases import Phrases
from journal.support.rejection import Rejection


@dataclass(frozen=True)
class Sequence(Model):
    """Steps the agent follows in order, one at a time, and the triggers that start it. Project-wide, so every environment can run it. One shipped with the journal is locked: shown, never changed or deleted."""

    text_fields: ClassVar[tuple[str, ...]] = ("title",)
    title: str = ""
    steps: tuple[SequenceStep, ...] = ()
    triggers: tuple[SequenceTrigger, ...] = ()
    end_condition: tuple[str, ...] = ()
    locked: bool = False

    def is_requested(self, text: str) -> bool:
        return any(trigger.trigger_type == SequenceTriggerType.PHRASE and Phrases.is_request(text, trigger.text) for trigger in self.triggers)

    def title_words(self) -> str:
        return self.title

    def unlocked(self) -> "Sequence":
        if self.locked:
            raise Rejection(f"sequence {self.id}, {self.title}, ships with the journal and is locked: it cannot be changed or deleted")
        return self
