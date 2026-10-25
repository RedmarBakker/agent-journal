import re
from typing import ClassVar
from dataclasses import dataclass

from journal.models.model import Model
from journal.models.trigger_action import TriggerAction

# a sequence starts on its phrase as the request itself, a short message and not a long one that happens to hold the words
REQUEST_EXTRA_TOKENS = 4


@dataclass(frozen=True)
class Trigger(Model):
    """Words the user chose, and what the journal does when one comes up in a prompt or a tool call."""

    text_fields: ClassVar[tuple[str, ...]] = ("phrases",)
    phrases: tuple[str, ...] = ()
    action: TriggerAction = TriggerAction.NUDGE
    text: str = ""

    def matches(self, text: str) -> bool:
        tokens = self.tokens(text)
        return any(self.is_request(tokens, self.tokens(phrase)) for phrase in self.phrases)

    def is_request(self, tokens: list[str], phrase: list[str]) -> bool:
        if not phrase or f" {' '.join(phrase)} " not in f" {' '.join(tokens)} ":
            return False
        return self.action != TriggerAction.SEQUENCE or len(tokens) - len(phrase) <= REQUEST_EXTRA_TOKENS

    @staticmethod
    def tokens(text: str) -> list[str]:
        return re.findall(r"[\w;/-]+", text.lower())

    def summary_line(self) -> str:
        return self.opening_line(self.text)
