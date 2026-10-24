from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.features.team.team_nudges import TeamNudges
from journal.features.team.team_part import TeamPart


class TeamConduct(Conduct):
    """The team feature's conduct in every state: at a session start, while the team is pinned to a newer journal version, the agent is informed once that this journal must be upgraded and its changes wait until then."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        upgrade = event.data.part(TeamPart).upgrade
        return self.none(TeamNudges.UPGRADE_NEEDED.create(line=upgrade)) if upgrade else self.none()

