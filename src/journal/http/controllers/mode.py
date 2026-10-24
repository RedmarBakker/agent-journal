from journal.http.support.request import Request
from journal.support.response import Response
from journal.support.rejection import Rejection
from journal.repositories.setting_rows import SettingRows
from journal.features.workers.workers_options import WorkersOptions


class ModeController:
    """The work mode the plan bar's Builder, Orchestrator and Solo buttons show and set: how the agent shares its work with workers."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def show(self, request: Request) -> Response:
        return Response.json({"mode": self.settings.option(WorkersOptions.MODE), "modes": list(WorkersOptions.MODE.choices)})

    def choose(self, request: Request) -> Response:
        mode = request.body.get("mode")
        if mode not in WorkersOptions.MODE.choices:
            raise Rejection(f"no such mode: {mode}; the modes are {', '.join(WorkersOptions.MODE.choices)}")
        self.settings.set(WorkersOptions.MODE.key, mode, request.actor)
        return self.show(request)
