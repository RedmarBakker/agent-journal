from pathlib import Path

from journal.engine.job import Job
from journal.events.announcer import Announcer
from journal.events.moments.output_view_changed import OutputViewChanged
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.features.shell.support.output_views import OutputViews
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.process_tree import ProcessTree
from journal.features.shell.support.output_silences import OutputSilences
from journal.features.shell.support.progress_stalls import ProgressStalls
from journal.features.shell.support.run_processes import RunProcesses
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope


class WatchRefresh(Job):
    """Every second the card of each watched output and of each one still running in the background is read again from its files, whatever its agent does, so the chat shows it moving, here and in a colleague's copy, which has the card but never the output; a card whose view has not changed is left as it is, and how long its progress stood still and how long it printed nothing are noted."""

    interval_seconds = 1.0

    def __init__(self, outputs: CommandOutputs, views: OutputViews, card: OutputProcessCard, announcer: Announcer, scope: Scope, stalls: ProgressStalls, processes: RunProcesses, silences: OutputSilences) -> None:
        self.outputs, self.views, self.card, self.announcer, self.scope, self.stalls, self.processes = outputs, views, card, announcer, scope, stalls, processes
        self.silences = silences

    def tick(self, time: float) -> None:
        carded = self.outputs.all_carded()
        shells = {output.row_id: OutputFiles(Path(output.folder)).shell_pid() for output in carded}
        tree = ProcessTree.read() if any(shells.values()) else ProcessTree([])
        for output in carded:
            if shells[output.row_id]:
                self.processes.sampled(output.row_id, tree.descendants(shells[output.row_id]))
            with self.scope.environment(output.environment_id):
                view = self.views.view(output)
                self.stalls.seen(output.row_id, view.fraction, time)
                if not output.ended:
                    self.silences.sampled(output.row_id, OutputFiles(Path(output.folder)).size(), output.creation_time.timestamp(), time)
                if view != self.card.card_view(output):
                    self.announcer.announce(OutputViewChanged(environment_id=output.environment_id, output=output.row_id))
