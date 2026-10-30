from journal.features.git.support.branch_holders import BranchHolders
from journal.models.environment import Environment


class StartRule:
    """Whether an agent may start in an environment: never on a branch another running environment works on."""

    def __init__(self, branches: BranchHolders) -> None:
        self.branches = branches

    def refusal(self, environment: Environment) -> str:
        return self.branches.start_refusal(environment)
