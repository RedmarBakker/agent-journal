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
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.command_classifier import CommandClassifier
from journal.support.timeout import Timeout

# how long a run's progress may stay complete, its command still running, before the agent is told
COMPLETE_WAIT_SECONDS = 60


class WatchRefresh(Job):
    """Every second the card of each watched output and of each one still running in the background is read again from its files, whatever its agent does, so the chat shows it moving, here and in a colleague's copy, which has the card but never the output; a card whose view has not changed is left as it is, and how long its progress stood still and how long it printed nothing are noted, and a run whose progress stays complete past a minute while its command goes on is marked on its row, once, which tells the agent."""

    interval_seconds = 1.0

    def __init__(self, outputs: CommandOutputs, views: OutputViews, card: OutputProcessCard, announcer: Announcer, scope: Scope, stalls: ProgressStalls, processes: RunProcesses, silences: OutputSilences, classifier: CommandClassifier) -> None:
        self.outputs, self.views, self.card, self.announcer, self.scope, self.stalls, self.processes = outputs, views, card, announcer, scope, stalls, processes
        self.silences, self.classifier = silences, classifier

    def tick(self, time: float) -> None:
        carded = self.outputs.all_carded()
        shells = {output.row_id: OutputFiles(Path(output.folder)).shell_pid() for output in carded}
        tree = ProcessTree.read() if any(shells.values()) else ProcessTree([])
        for output in carded:
            if shells[output.row_id]:
                self.processes.sampled(output.row_id, tree.descendants(shells[output.row_id]), self.classifier)
            with self.scope.environment(output.environment_id):
                view = self.views.view(output)
                self.stalls.seen(output.row_id, view.fraction, time)
                if self.is_complete_unreported(output, time):
                    output = self.outputs.save(output.complete_reported(time, int(self.stalls.complete_seconds(output.row_id, time))), Actor.system())
                    view = self.views.view(output)
                if not output.ended:
                    self.silences.sampled(output.row_id, OutputFiles(Path(output.folder)).size(), output.creation_time.timestamp(), time)
                if view != self.card.card_view(output):
                    self.announcer.announce(OutputViewChanged(environment_id=output.environment_id, output=output.row_id))

    def is_complete_unreported(self, output: CommandOutput, time: float) -> bool:
        return not output.ended and not output.is_complete_reported and self.stalls.is_long_complete(output.row_id, Timeout.seconds(COMPLETE_WAIT_SECONDS), time)
