from journal.models.environment import Environment
from journal.sync.team_account import TeamAccount


class WorktreeHosts:
    """Which machine holds an environment's worktree folder: the one that launched it there, named on the environment so the whole team knows; only that machine launches into it or removes it."""

    def __init__(self, account: TeamAccount) -> None:
        self.account = account

    def local_machine(self) -> str:
        return self.account.device_name()

    def host_machine(self, environment: Environment) -> str:
        return environment.worktree_host if environment.worktree_host and environment.worktree_host != self.local_machine() else ""

    def refusal(self, environment: Environment, action: str) -> str:
        host = self.host_machine(environment)
        return f"the worktree of {environment.name} is on the machine {host}: {action} it there" if host else ""
