from journal.features.git.support.branch_holders import BranchHolders
from journal.features.git.support.worktree_hosts import WorktreeHosts
from journal.models.environment import Environment
from journal.repositories.environment_owners import EnvironmentOwners
from journal.sync.hosting import Hosting
from journal.sync.team_chat import TeamChat

HOSTED_REFUSAL = "this journal is hosted for the team's browsers; agents run on a member's own journal"


class StartRule:
    """Whether an agent may start here: never on a hosted journal, never in a colleague's environment, in the Team chat or a worktree only on the machine that holds it, and never on a branch another running environment works on."""

    def __init__(self, hosting: Hosting, owners: EnvironmentOwners, chat: TeamChat, branches: BranchHolders, hosts: WorktreeHosts) -> None:
        self.hosting, self.owners, self.chat, self.branches, self.hosts = hosting, owners, chat, branches, hosts

    def refusal(self, environment: Environment, person: int) -> str:
        return self.hosted_refusal() or self.owners.start_refusal(environment, person) or self.chat.start_refusal(environment) or self.hosts.refusal(environment, "launch") or self.branches.start_refusal(environment)

    def hosted_refusal(self) -> str:
        return HOSTED_REFUSAL if self.hosting.is_hosted() else ""
