from contextvars import ContextVar

from journal.events.models.created import Created
from journal.events.listener import Listener
from journal.support.actor_type import ActorType
from journal.models.command_output import CommandOutput
from journal.models.entry import Entry
from journal.models.link import Link
from journal.models.model import Model
from journal.models.outgoing_change import OutgoingChange
from journal.models.task_log import TaskLog

RECORD_ROWS = (Entry, CommandOutput, OutgoingChange, Link, TaskLog)
RUN: ContextVar[list | None] = ContextVar("creations", default=None)


class Creations(Listener[Created]):
    """Every row made while a command runs, by the command or by what its events caused, so the agent is informed the name and number of each it may address next; the record's own rows, a link, a queued change, a log line, are left out."""

    def handle(self, event: Created) -> None:
        produced = RUN.get()
        if produced is not None and event.actor.kind != ActorType.SYSTEM and not isinstance(event.model, RECORD_ROWS):
            produced.append(event.model)

    @staticmethod
    def begin() -> list[Model]:
        produced: list[Model] = []
        RUN.set(produced)
        return produced

    @staticmethod
    def end() -> None:
        RUN.set(None)

    @classmethod
    def line(cls, produced: list[Model], line_text: str) -> str:
        anonymous = [name for m in produced if (name := cls.lookup(m)) not in line_text]
        return "created: " + ", ".join(anonymous) if anonymous else ""

    @staticmethod
    def lookup(produced: Model) -> str:
        return f"{produced.noun()} {produced.id}"
