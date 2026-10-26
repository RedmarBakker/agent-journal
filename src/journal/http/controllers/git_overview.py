from journal.http.git.git_overview import GitOverview
from journal.http.support.request import Request
from journal.support.response import Response

PAGE_ROWS = 30


class GitOverviewController:
    """The Git page's three lists, read only: the branches, the recent commits of the current branch and the open pull requests."""

    def __init__(self, overview: GitOverview) -> None:
        self.overview = overview

    def branches(self, request: Request) -> Response:
        return Response.json(self.overview.branches(*self.paging(request)))

    def commits(self, request: Request) -> Response:
        return Response.json(self.overview.commits(*self.paging(request)))

    def pulls(self, request: Request) -> Response:
        return Response.json(self.overview.pull_requests())

    @staticmethod
    def paging(request: Request) -> tuple[int, int]:
        offset, last = request.query.get("skip", ""), request.query.get("last", "")
        return int(offset) if offset.isdigit() else 0, int(last) if last.isdigit() and int(last) > 0 else PAGE_ROWS
