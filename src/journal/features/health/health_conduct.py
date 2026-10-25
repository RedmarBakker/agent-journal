from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.feature_data import FeatureData
from journal.features.health.health_nudges import HealthNudges
from journal.features.health.health_part import HealthPart


class HealthConduct(Conduct):
    """The health feature's conduct in every state: when the journal answers again, the agent's next event carries one line naming the hooks and shell commands that went through unchecked while it did not, and asks it to check them."""

    def on_agent_event(self, event: AgentEvent, settings: Settings) -> Transition:
        return self.none(*unchecked_lines(event.data))


def unchecked_lines(data: FeatureData) -> list[Nudge]:
    work = data.part(HealthPart)
    return [] if work.is_empty() else [HealthNudges.UNCHECKED_WORK.create(kinds=work.kinds_text(), commands=work.commands_text() or "none of them named")]
