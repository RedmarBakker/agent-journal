from pathlib import Path

from journal.engine.support.launch_files import LaunchFiles
from journal.engine.support.lazy_facts import LazyFacts
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.features.briefing.support.start_lines import StartLines
from journal.models.agent import Agent
from journal.repositories.environments import Environments
from journal.repositories.rules import Rules


class BriefingDataReader:
    """Reads the briefing feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields BriefingData names."""

    def __init__(self, start: StartLines, environments: Environments, rules: Rules, launches: LaunchFiles, scope: Scope, stages: StageTimes) -> None:
        self.start, self.environments, self.rules, self.launches, self.scope, self.stages = start, environments, rules, launches, scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        facts = LazyFacts("briefing", {
            "is_overview_read": lambda: agent.is_overview_read,
            "environment_row": lambda: self.environments.find(agent.environment_id),
            "environment": lambda: facts.environment_row.name,
            "peer_session_active_at": lambda: self.start.other_session_time(agent.session),
            "rules": self.start.rules_numbered,
            "rules_count": lambda: len(self.rules.all()),
            "memories": self.start.memories_weighed,
            "reminders": self.start.reminders_numbered,
            "waiting": self.start.waiting,
            "team_history": lambda: self.start.team_history(facts.environment_row),
            "interrupted_runs": self.start.interrupted_runs,
            "launch_folder": lambda: self.launches.folder(facts.environment),
            "is_launch_folder_missing": lambda: bool(facts.launch_folder) and not Path(facts.launch_folder).is_dir(),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts
