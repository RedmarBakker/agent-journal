from datetime import datetime, timezone
from pathlib import Path

from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.shell.support.activity_label import LONG_RUNS, ActivityLabel
from journal.features.shell.support.count_forms import CountForms
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.output_views import OutputViews
from journal.features.shell.support.readers import Readers
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.support.actor import Actor

TOTAL_WAIT_SECONDS = 60


class UntotaledRunRecord(AgentListener[Ticked]):
    """A running test run or build of the agent's whose reader has shown no progress for a minute is marked on its row, once per revision of the reader, and the mark raises OutputTotalMissing, which tells the agent, with the pattern that reads the run's count when it prints one."""

    def __init__(self, outputs: CommandOutputs, views: OutputViews, labels: ActivityLabel, readers: Readers) -> None:
        self.outputs, self.views, self.labels, self.readers = outputs, views, labels, readers

    def handle(self, event: Ticked) -> None:
        latest_start = datetime.fromtimestamp(event.time - TOTAL_WAIT_SECONDS, timezone.utc)
        for output in self.outputs.total_request_candidates(event.session, latest_start):
            self.request_total(output, event.time)

    def request_total(self, output: CommandOutput, time: float) -> None:
        revision = self.readers.file_stamp(output.watch_reader)
        if self.is_total_missing(output, revision):
            self.outputs.save(output.total_requested(time, revision, self.count_pattern(output)), Actor.system())

    def is_total_missing(self, output: CommandOutput, revision: float) -> bool:
        return self.labels.line_label(output.command) in LONG_RUNS and not self.outputs.has_total_request(output.watch_reader, revision) and self.has_no_bar(output)

    def has_no_bar(self, output: CommandOutput) -> bool:
        view = self.views.view(output)
        return bool(view.lines) and not view.fraction

    @staticmethod
    def count_pattern(output: CommandOutput) -> str:
        form = CountForms.form(OutputFiles(Path(output.folder)).lines())
        return form.progress if form else ""
