from pathlib import Path

from journal.engine.support.launch_files import LaunchFiles
from journal.features.briefing.support.briefing_data import BriefingData
from journal.features.briefing.support.start_lines import StartLines
from journal.models.agent import Agent
from journal.repositories.environments import Environments
from journal.repositories.rules import Rules


class BriefingDataReader:
    """Reads the briefing feature's part of the feature data for an agent."""

    def __init__(self, start: StartLines, environments: Environments, rules: Rules, launches: LaunchFiles) -> None:
        self.start, self.environments, self.rules, self.launches = start, environments, rules, launches

    def read(self, agent: Agent) -> BriefingData:
        environment = self.environments.find(agent.environment_id)
        return BriefingData(is_overview_read=agent.is_overview_read, environment=environment.name, peer_session_active_at=self.start.other_session_time(agent.session), rules=self.start.rules_numbered(), rules_count=len(self.rules.all()), facts=self.start.facts_numbered(), reminders=self.start.reminders_numbered(), waiting=self.start.waiting(), team_history=self.start.team_history(environment), interrupted_runs=self.start.interrupted_runs(), launch_folder=(folder := self.launches.folder(environment.name)), is_launch_folder_gone=bool(folder) and not Path(folder).is_dir())
