from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.session_started import SessionStarted
from journal.events.feature_data import FeatureData
from journal.features.health.health_nudges import HealthNudges
from journal.features.health.health_part import HealthPart
from journal.features.health.support.unchecked_work import UncheckedWork


class HealthConduct(Conduct):
    """The health feature's conduct in every state: when the journal answers again, the agent's next event carries one line naming the hooks and shell commands that went through unchecked while it did not, and asks it to check them; in the journal's own repository a session start, never one after a compaction, tells it to start the panic watch, since a cron job ends with its session."""

    def on_agent_event(self, event: AgentEvent, settings: Settings) -> Transition:
        return self.none(*unchecked_lines(event.data))

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        if event.is_compaction_start():
            return self.none()
        return self.none(*panic_watch_lines(event.data.part(HealthPart)))


def unchecked_lines(data: FeatureData) -> list[Nudge]:
    work = data.part(HealthPart)
    if work.is_empty():
        return []
    return [HealthNudges.UNCHECKED_WORK.create(kinds=work.kinds_text(), commands=work.commands_text() or "none of them named")]


def panic_watch_lines(work: UncheckedWork) -> list[Nudge]:
    return [HealthNudges.PANIC_WATCH.create()] if work.journal_repository else []
