from typing import ClassVar
from dataclasses import dataclass

from journal.events.rows.row_resolved import RowResolved
from journal.models.scoped import Scoped


ACTIVE = "running"
FINISHED = "finished"
FAILED = "failed"
# a run is shown in the chat only once it has gone on this long; one that ends sooner never reaches it
MARK_SECONDS = 3.0


@dataclass(frozen=True)
class CommandOutput(Scoped):
    """A shell line the runner ran, numbered by its row: the agent's own command, the folder holding each part's output, and, once it was moved to the background, how it ended, whether the journal's restart cut it off, and whether its agent watches it through a reader, whether its agent has read it since it ended, and what its reader picked from it at its end; an end a standing wait names is informed by the wait's own end. Lines about it name only its number."""

    shared: ClassVar[bool] = False

    chain: str = ""
    command: str = ""
    session: str | None = None
    folder: str = ""
    moved: bool = False
    ended: bool = False
    status: int = 0
    is_announced: bool = False
    is_read: bool = False
    is_interrupted: bool = False
    is_watched: bool = False
    watch_reader: str = ""
    watch_title: str = ""
    summary: str | None = None

    def run_seconds(self) -> float:
        return (self.update_time - self.creation_time).total_seconds()

    def is_past_mark(self, time: float) -> bool:
        return self.moved or time - self.creation_time.timestamp() >= MARK_SECONDS

    def headline(self) -> str:
        first, *remainder = self.command.splitlines() or [""]
        return f"{first} (and {len(remainder)} more lines)" if remainder else first

    def backgrounded(self) -> "CommandOutput":
        return self.with_(moved=True)

    def ended_with(self, status: int, time: float, summary: str | None = None) -> "CommandOutput":
        ended = self.with_(ended=True, status=status, summary=summary)
        return ended.with_event(RowResolved(environment_id=self.environment_id, time=time, ref=f"{self.table()}:{self.id}", outcome=ended.outcome()))

    def interrupted(self, time: float) -> "CommandOutput":
        ended = self.with_(ended=True, is_interrupted=True)
        return ended.with_event(RowResolved(environment_id=self.environment_id, time=time, ref=f"{self.table()}:{self.id}", outcome=ended.outcome()))

    def wait_end(self, status: int, time: float, summary: str | None) -> "CommandOutput":
        return self.ended_with(status, time, summary).announced()

    def announced(self) -> "CommandOutput":
        return self.with_(is_announced=True)

    def seen(self) -> "CommandOutput":
        return self.with_(is_read=True)

    def watched(self, reader: str, title: str) -> "CommandOutput":
        return self.with_(is_watched=True, watch_reader=reader, watch_title=title)

    def unwatched(self) -> "CommandOutput":
        return self.with_(is_watched=False)

    def is_resolved(self) -> bool:
        return self.ended

    def is_success(self) -> bool:
        return self.ended and self.status == 0 and not self.is_interrupted

    def stage(self) -> str:
        if not self.ended:
            return ACTIVE
        return FINISHED if self.is_success() else FAILED

    def ending(self) -> str:
        if self.is_interrupted:
            return "cut off when the journal restarted"
        return "finished" if self.status == 0 else f"failed with code {self.status}"

    def outcome(self) -> str:
        return f"output {self.id} {self.ending()}" if self.summary is None else f"output {self.id} {self.ending()}: {self.summary}"
