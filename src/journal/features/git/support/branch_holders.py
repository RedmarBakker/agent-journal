import subprocess

from journal.config import Config
from journal.models.environment import Environment
from journal.repositories.environments import Environments
from journal.support.worktree import Worktree
from journal.supervisor_link import SupervisorLink

GIT_SECONDS = 10


class BranchHolders:
    """Which branch each environment with a running agent works on: the branch of its own worktree, or the main checkout's when it works there; no two running environments work on one branch."""

    def __init__(self, config: Config, environments: Environments, supervisor: SupervisorLink) -> None:
        self.root, self.environments, self.supervisor = config.root, environments, supervisor

    def checkout_branch(self, environment: Environment) -> str:
        folder = Worktree(self.root, environment.name).folder
        return subprocess.run(["git", "-C", str(folder), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=GIT_SECONDS).stdout.strip()

    def branch_environments(self, environment: Environment) -> dict[str, str]:
        active = [candidate for candidate in self.supervisor.running(self.environments.working()) if candidate.row_id != environment.row_id]
        return {branch: candidate.name for candidate in active if (branch := self.checkout_branch(candidate))}

    def start_refusal(self, environment: Environment) -> str:
        branch = self.checkout_branch(environment)
        holder = self.branch_environments(environment).get(branch, "")
        if not holder:
            return ""
        return f"{holder} is running on branch {branch}, which {environment.name} would work on too: start {environment.name} in a worktree of its own, or switch {holder} to another branch first"
