from dataclasses import asdict
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.output_view import OutputView
from journal.http.support.output_menu_entry import OutputMenuEntry
from journal.repositories.messages import Messages
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.support.rejection import Rejection
from journal.support.response import Response
from journal.repositories.command_outputs import CommandOutputs


PAGE_LINES = 500
USER_STOP_LINE = "journal: this run was stopped by the user from the chat"


class OutputController:
    """The outputs still running in the environment, each with its card and whether it is docked; what one stored output holds, for the viewer: its command, how it ended and one page of what it printed, the newest by default, the lines after a position (`after`) or the page before one (`before`), with the position it starts at and the next one to ask from; and the stop of a run still going, which kills its process group."""

    def __init__(self, outputs: CommandOutputs, messages: Messages, scope: Scope) -> None:
        self.outputs, self.messages, self.scope = outputs, messages, scope

    def running(self, request: Request) -> Response:
        return Response.json({"outputs": [asdict(OutputMenuEntry.build(output, self.messages.keyed(OutputView.key(output.row_id), Actor.system()))) for output in self.outputs.running(self.scope.id)]})

    def show(self, request: Request) -> Response:
        output = self.outputs.find(request.number("id"))
        files = OutputFiles(Path(output.folder))
        stored = files.is_stored()
        start, size = self.window(request, files.line_count() if stored else 0)
        lines = files.page(start, size) if stored else []
        return Response.json({**ModelFields.build(output), "outcome": files.outcome() if stored else "files gone", "lines": lines, "start": start, "next": start + len(lines)})

    def stop(self, request: Request) -> Response:
        output = self.outputs.find(request.number("id"))
        files = OutputFiles(Path(output.folder))
        if not files.is_stored():
            raise Rejection(f"output {output.id} keeps no files of its run, so there is nothing of it to stop")
        files.stop(USER_STOP_LINE)
        return Response.json(ModelFields.build(output))

    @staticmethod
    def window(request: Request, total: int) -> tuple[int, int]:
        size = int(request.queried("limit", PAGE_LINES))
        if "after" in request.query:
            return int(request.queried("after")), size
        if "before" in request.query:
            end = int(request.queried("before"))
            return max(0, end - size), min(size, end)
        return max(0, total - size), size
