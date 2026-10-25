from journal.features.checks.support.git_hooks import GitHooks
from journal.http.support.request import Request
from journal.support.response import Response


class GitHookController:
    """The repository's git hooks, for the Checks page: each by its name, whether it is active, and what it runs; read only."""

    def __init__(self, hooks: GitHooks) -> None:
        self.hooks = hooks

    def index(self, request: Request) -> Response:
        return Response.json([hook.as_data() for hook in self.hooks.listed()])
