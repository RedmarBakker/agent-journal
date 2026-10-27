from pathlib import Path

from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.output_views import OutputViews
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.process_check import ProcessCheck


class StoppedOutputEnd(AgentListener[Ticked]):
    """At each tick a command not ended whose heartbeat stopped is ended as cut off, and so is one whose shell process is gone though its heartbeat still beats, with what its reader last picked from its output as its summary, so a command whose processes vanished never lingers as running or holds a restart."""

    def __init__(self, outputs: CommandOutputs, views: OutputViews, scope: Scope) -> None:
        self.outputs, self.views, self.scope = outputs, views, scope

    def handle(self, event: Ticked) -> None:
        for output in self.outputs.stopped_outputs():
            self.outputs.save(output.interrupted(event.time), Actor.system())
        for output in self.outputs.unended():
            if self.has_lost_shell(Path(output.folder)):
                with self.scope.environment(output.environment_id):
                    self.outputs.save(output.with_(summary=self.views.ended_summary(output)).interrupted(event.time), Actor.system())

    @staticmethod
    def has_lost_shell(folder: Path) -> bool:
        pid = OutputFiles(folder).shell_pid()
        return folder.is_dir() and not (folder / "done").is_file() and 0 < pid and not ProcessCheck.is_running(pid)
