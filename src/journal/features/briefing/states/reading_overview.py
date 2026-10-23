from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.overview_read import OverviewRead
from journal.features.skills.skills_conduct import is_skill_read, skills_feature

OVERVIEW_COMMAND = "journal environment overview"


@dataclass(frozen=True)
class ReadingOverview(BaseState):
    """After a compaction the agent reads the overview before anything else: every tool use and every journal command is refused, but a read of a skill it has to read and journal environment overview itself; it pops once the overview has run."""

    name = "reading_overview"
    title = "Reading the overview"

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if event.subagent or event.call.command.strip().startswith(OVERVIEW_COMMAND) or is_skill_read(event, event.data.part(skills_feature()).debt_cards()):
            return self.none()
        from journal.features.briefing.feature import Briefing
        return self.refuse(Briefing.OVERVIEW_FIRST.create())

    def on_overview_read(self, event: OverviewRead, settings: Settings) -> Transition:
        return self.pop()
