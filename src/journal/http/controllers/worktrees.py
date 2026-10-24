from journal.features.git.support.launch_worktrees import LaunchWorktrees
from journal.features.git.support.worktree_removal import WorktreeRemoval
from journal.http.support.request import Request
from journal.support.response import Response
from journal.sync.hosting import Hosting


class WorktreeController:
    """The worktrees launches made whose environment is gone, for the viewer to list beside the environments, each removed through the same checks as journal worktree remove; the hosted journal has no checkout and lists none."""

    def __init__(self, worktrees: LaunchWorktrees, removal: WorktreeRemoval, hosting: Hosting) -> None:
        self.worktrees, self.removal, self.hosting = worktrees, removal, hosting

    def index(self, request: Request) -> Response:
        left = [] if self.hosting.is_hosted() else self.worktrees.left()
        return Response.json({"worktrees": [{"name": tree.name, "branch": tree.current_branch()} for tree in left]})

    def removal_of(self, request: Request) -> Response:
        return Response.json({"line": self.removal.removed(request.params["name"])})
