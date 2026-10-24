from journal.config import Config
from journal.events.agent.session_ended import SessionEnded
from journal.events.agent_listener import AgentListener
from journal.repositories.environments import Environments
from journal.support.worktree import Worktree


class WorktreeTipRecord(AgentListener[SessionEnded]):
    """A session's end in an environment with a worktree keeps where its branch stands, so a worktree whose folder is lost is made again from there."""

    def __init__(self, config: Config, environments: Environments) -> None:
        self.config, self.environments = config, environments

    def handle(self, event: SessionEnded) -> None:
        tree = Worktree(self.config.root, self.environments.find(event.environment_id).name)
        if tree.path.is_dir():
            tree.record_tip()
