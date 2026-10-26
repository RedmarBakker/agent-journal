from typing import ClassVar
from journal.support.task_notification import TaskNotification
from dataclasses import dataclass

from journal.models.scoped import Scoped
from journal.models.subagent_state import SubagentState

CURRENT_SECONDS = 60.0


@dataclass(frozen=True)
class Subagent(Scoped):
    """A subagent an agent dispatched: the dispatch entry it was loaded from, what it was asked to do, its type and model, its own session once known, its status, and the tool's error when the dispatch failed. Ended is a subagent from before the journal stored these rows whose end it never saw."""

    text_fields: ClassVar[tuple[str, ...]] = ("task", "brief")
    unshown_fields: ClassVar[tuple[str, ...]] = ("transcript_bytes",)
    dispatch: str = ""
    dispatcher: str = ""
    task: str = ""
    brief: str = ""
    agent_type: str = "subagent"
    model: str | None = None
    session: str = ""
    state: SubagentState = SubagentState.ACTIVE
    started_at: float = 0.0
    ended_at: float = 0.0
    resumed_at: float = 0.0
    reason: str = ""
    transcript_bytes: int = 0

    def title_words(self) -> str:
        return self.task

    def is_running(self) -> bool:
        return self.state == SubagentState.ACTIVE

    def is_idle(self) -> bool:
        return bool(self.session) and self.state in (SubagentState.FINISHED, SubagentState.STOPPED, SubagentState.ENDED)

    def is_current(self, time: float) -> bool:
        return self.is_running() or time - self.ended_at < CURRENT_SECONDS

    def answered(self, session: str) -> "Subagent":
        return self.with_(session=session)

    def finished(self, state: SubagentState, time: float) -> "Subagent":
        return self.with_(state=state, ended_at=time)

    def notified(self, notification: TaskNotification, time: float) -> "Subagent":
        if notification.is_failed():
            return self.failed(notification.summary, time)
        if notification.is_refusal():
            return self.with_(state=SubagentState.UNFINISHED, ended_at=time, reason=notification.first_line())
        return self.finished(SubagentState.FINISHED, time)

    def failed(self, reason: str, time: float) -> "Subagent":
        return self.with_(state=SubagentState.FAILED, ended_at=time, reason=reason)

    def resumed(self, time: float, job: str) -> "Subagent":
        return self.with_(state=SubagentState.ACTIVE, ended_at=0.0, resumed_at=time, brief=f"{self.brief} {job}")

    def retired(self, time: float) -> "Subagent":
        return self.with_(state=SubagentState.RETIRED, ended_at=time)

    def recorded(self, paired: "Subagent") -> "Subagent":
        if self.state == SubagentState.RETIRED and paired.resumed_at <= self.ended_at:
            return self
        return self.with_(session=paired.session, state=paired.state, ended_at=paired.ended_at, resumed_at=paired.resumed_at, reason=paired.reason)
