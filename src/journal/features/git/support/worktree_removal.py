from journal.config import Config
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.support.rejection import Rejection
from journal.support.worktree import Worktree
from journal.support.workspace_worktree import WorkspaceWorktree


class WorktreeRemoval:
    """The one way a launch's worktree is removed, by the command and the viewer alike: refused while a session works in it or while it holds uncommitted work; its branch and last commit kept so a launch of its name makes it again."""

    def __init__(self, config: Config, environments: Environments, agents: Agents) -> None:
        self.config, self.environments, self.agents = config, environments, agents

    def worktree(self, name: str) -> Worktree:
        return WorkspaceWorktree.chosen(self.config.root, name)

    def removed(self, name: str) -> str:
        tree = self.worktree(name)
        refusal = self.refusal(tree)
        if refusal:
            raise Rejection(refusal)
        tree.removed()
        return f"removed the worktree {tree.path}; its branch {tree.branch} and its last commit stay, and journal claude --worktree {tree.name} makes it again from there"

    def refusal(self, tree: Worktree) -> str:
        if not tree.path.is_dir():
            return f"there is no worktree named {tree.name} at {tree.path}"
        if [agent for environment in self.environments.matching(name=tree.name) for agent in self.agents.unended_scoped(environment.row_id)]:
            return f"a session works in the worktree {tree.name}: end it first, then remove the worktree"
        uncommitted = tree.uncommitted()
        if uncommitted:
            return f"the worktree {tree.name} holds {len(uncommitted)} uncommitted files ({', '.join(uncommitted[:5])}): commit or remove them first"
        return ""
