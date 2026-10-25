import re

from journal.console.console import Console
from journal.events.listener import Listener
from journal.events.models.model_event import ModelEvent
from journal.events.models.updated import Updated
from journal.features.verification.commands.verdict_command import REFUTED_VERDICT, SOUND_VERDICT
from journal.models.verifier import Verifier
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.support.caller import Caller

TYPED_VERDICT = re.compile(rf"""journal verdict ({SOUND_VERDICT}|{REFUTED_VERDICT}) (?:"([^"\n]+)"|'([^'\n]+)')""")
TYPED_NOTE = " (the verifier typed this verdict instead of running it)"


class TypedVerdict(Listener[ModelEvent]):
    """A verifier whose session ended with no verdict, its last words exactly one journal verdict yes or no line, has that verdict recorded as if it had run it, through the verdict command, its reason saying it was typed."""

    def __init__(self, entries: Entries, environments: Environments, console: Console) -> None:
        self.entries, self.environments, self.console = entries, environments, console

    def handle(self, event: ModelEvent) -> None:
        if not isinstance(event, Updated) or not isinstance(event.model, Verifier) or not event.model.has_ended():
            return
        verifier = event.model
        said = TYPED_VERDICT.fullmatch(self.entries.last_words(verifier.session).strip())
        if said:
            caller = Caller.verifier(self.environments.find(verifier.environment_id).name, verifier.id, verifier.session, verifier.provider)
            self.console.run(["verdict", said.group(1), (said.group(2) or said.group(3)) + TYPED_NOTE], caller)
