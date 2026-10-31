from journal.http.support.request import Request
from journal.support.response import Response
from journal.http.support.viewer_presence import ViewerPresence
from journal.repositories.environments import Environments


class ViewerController:
    """Whether a viewer tab is open on this journal."""

    def __init__(self, presence: ViewerPresence, environments: Environments) -> None:
        self.presence, self.environments = presence, environments

    def show(self, request: Request) -> Response:
        return Response.json({"open": self.presence.open()})

    def launch(self, request: Request) -> Response:
        environment = request.body.get("environment", "") if isinstance(request.body, dict) else ""
        if not isinstance(environment, str) or not environment:
            return Response.refused("the launch names an environment")
        self.environments.existing(environment)
        return Response.json({"sequence": self.presence.switch_to(environment)})
