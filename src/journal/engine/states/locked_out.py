from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.engine_nudges import EngineNudges
from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.compacting import Compacting
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_starting import ToolStarting
from journal.support.lockout_option import LOCKOUT_OPTION
from journal.support.timeout import Timeout

# how long the journal answers again before a worker locked out goes on
STEADY = Timeout.seconds(5)


@dataclass(frozen=True)
class LockedOut(BaseState):
    """A worker whose journal stopped answering at silence_start and answered again at return_time: every tool is held and nothing is pushed over it, a compaction of its context included, and it pops once the journal has answered for STEADY, or, when the silence outlasted the grace the Settings page sets, it ends the worker, every tool held and its stop let through."""

    name = "locked_out"
    assigner = NoTaskAssigner
    title = "Locked out of the journal"
    conduct_free = True
    silence_start: float = 0.0
    return_time: float = 0.0

    def takes_pushes(self) -> bool:
        return False

    def silence_seconds(self) -> int:
        return round(self.return_time - self.silence_start)

    def is_expired(self, settings: Settings) -> bool:
        return Timeout.seconds(settings.integer(LOCKOUT_OPTION)).started(self.silence_start).is_elapsed(self.return_time)

    def is_steady(self, moment: float) -> bool:
        return STEADY.started(self.return_time).is_elapsed(moment)

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if self.is_expired(settings):
            return self.refuse(EngineNudges.LOCKOUT_END.create(seconds=self.silence_seconds(), grace=settings.integer(LOCKOUT_OPTION)))
        if self.is_steady(event.time):
            return self.forward()
        return self.refuse(EngineNudges.LOCKOUT_WAIT.create(seconds=self.silence_seconds()))

    def on_compacting(self, event: Compacting, settings: Settings) -> Transition:
        event.stop_propagation()
        return self.none()

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        return self.pop() if self.is_steady(event.time) and not self.is_expired(settings) else self.none()
