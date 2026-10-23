from typing import ClassVar

from journal.features.git.support.branch_holders import BranchHolders
from journal.features.git.support.branch_environments import BranchEnvironments
from journal.models.agent import Agent
from journal.repositories.environments import Environments


class BranchEnvironmentsReader:
    """Answers which branches the other running environments work on, for the agent's own environment."""

    source: ClassVar[type[BranchEnvironments]] = BranchEnvironments

    def __init__(self, holders: BranchHolders, environments: Environments) -> None:
        self.holders, self.environments = holders, environments

    def read(self, agent: Agent) -> dict:
        return self.holders.branch_environments(self.environments.find(agent.environment_id))
