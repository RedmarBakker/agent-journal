from contextvars import ContextVar

from journal.console.creation_capture import CreationCapture
from journal.events.models.created import Created
from journal.events.listener import Listener
from journal.models.command_output import CommandOutput
from journal.models.entry import Entry
from journal.models.link import Link
from journal.models.model import Model
from journal.models.outgoing_change import OutgoingChange
from journal.models.state_transition import StateTransition
from journal.models.task_log import TaskLog

RECORD_ROWS = (Entry, CommandOutput, OutgoingChange, Link, TaskLog, StateTransition)
RUN: ContextVar[CreationCapture | None] = ContextVar("creations", default=None)


class Creations(Listener[Created]):
    """Every row made while a command runs, by the command or by what its events caused, so the agent is informed the name and number of each it may address next; the record's own rows, a link, a queued change, a log line, a count of a kind of stack change, are left out."""

    def handle(self, event: Created) -> None:
        capture = RUN.get()
        if capture is not None and not event.actor.is_system_actor() and not isinstance(event.model, RECORD_ROWS):
            capture.record(event.model)

    @staticmethod
    def begin() -> CreationCapture:
        capture = CreationCapture()
        RUN.set(capture)
        return capture

    @staticmethod
    def end(capture: CreationCapture) -> list[Model]:
        produced = capture.close()
        RUN.set(None)
        return produced

    @classmethod
    def line(cls, produced: list[Model], line_text: str) -> str:
        anonymous = [name for m in produced if (name := cls.lookup(m)) not in line_text]
        return "created: " + ", ".join(anonymous) if anonymous else ""

    @staticmethod
    def lookup(produced: Model) -> str:
        return f"{produced.noun()} {produced.id}"
