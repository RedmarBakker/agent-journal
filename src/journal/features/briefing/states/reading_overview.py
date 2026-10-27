from dataclasses import dataclass

from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.overview_read import OverviewRead
from journal.features.skills.skills_conduct import is_skill_read, skill_paths
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.skills.skills_part import SkillsPart
from journal.features.briefing.briefing_nudges import BriefingNudges

OVERVIEW_COMMAND = "journal environment overview"


@dataclass(frozen=True)
class ReadingOverview(BaseState):
    """After a compaction the agent reads the overview before anything else: every tool use and every journal command is refused, but a read of a skill it has to read and journal environment overview itself, with one line that names every skill still unread_skills and the overview, in either order, and no other line beside it; it pops once the overview has run."""

    name = "reading_overview"
    assigner = NoTaskAssigner
    title = "Reading the overview"

    def takes_pushes(self) -> bool:
        return False

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        unread_skills = event.data.part(SkillsPart).debt_cards()
        if event.call.command.strip().startswith(OVERVIEW_COMMAND) or is_skill_read(event, unread_skills):
            return self.none()
        event.stop_propagation()
        return self.refuse(BriefingNudges.SKILLS_AND_OVERVIEW_REQUEST.create(skills=SkillsNudges.listed(skill_paths(unread_skills))) if unread_skills else BriefingNudges.OVERVIEW_FIRST.create())

    def on_overview_read(self, event: OverviewRead, settings: Settings) -> Transition:
        return self.pop()
