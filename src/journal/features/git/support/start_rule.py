from journal.features.git.support.branch_holders import BranchHolders
from journal.features.git.support.worktree_hosts import WorktreeHosts
from journal.models.environment import Environment


class StartRule:
    """Whether an agent may start in an environment: a worktree only on the machine that holds it, and never on a branch another running environment works on."""

    def __init__(self, branches: BranchHolders, hosts: WorktreeHosts) -> None:
        self.branches, self.hosts = branches, hosts

    def refusal(self, environment: Environment, person: int) -> str:
        return self.hosts.refusal(environment, "launch") or self.branches.start_refusal(environment)
