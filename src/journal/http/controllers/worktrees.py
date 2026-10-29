from journal.features.git.support.launch_worktrees import LaunchWorktrees
from journal.features.git.support.worktree_removal import WorktreeRemoval
from journal.http.support.request import Request
from journal.support.response import Response


class WorktreeController:
    """The worktrees launches made whose environment is gone, for the viewer to list beside the environments, each removed through the same checks as journal worktree remove."""

    def __init__(self, worktrees: LaunchWorktrees, removal: WorktreeRemoval) -> None:
        self.worktrees, self.removal = worktrees, removal

    def index(self, request: Request) -> Response:
        orphans = self.worktrees.orphan_worktrees()
        return Response.json({"worktrees": [{"name": tree.name, "branch": tree.current_branch()} for tree in orphans]})

    def worktree_removal(self, request: Request) -> Response:
        return Response.json({"line": self.removal.removed(request.params["name"])})
