from pathlib import Path

from journal.features.shell.support.activity_label import LONG_RUNS, ActivityLabel
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.silent_run import SilentRun
from journal.repositories.command_outputs import CommandOutputs
from journal.support.time_source import TimeSource

# how long a background run may print nothing before the agent is told its command holds its output back
QUIET_SECONDS = 20


class SilentRuns:
    """The agent's background test runs and builds that have printed nothing at all for QUIET_SECONDS or more since they began: a buffered command, never a run that is only slow between its lines, nor a command that prints nothing by its nature, such as a sleep."""

    def __init__(self, outputs: CommandOutputs, time_source: TimeSource, labels: ActivityLabel) -> None:
        self.labels = labels
        self.outputs, self.time_source = outputs, time_source

    def running(self, session: str) -> tuple[SilentRun, ...]:
        now = self.time_source.seconds()
        unprinted = [output for output in self.outputs.background(session) if self.labels.line_label(output.command) in LONG_RUNS and OutputFiles(Path(output.folder)).size() == 0]
        return tuple(SilentRun(output.row_id, output.command, int(now - output.creation_time.timestamp())) for output in unprinted if now - output.creation_time.timestamp() >= QUIET_SECONDS)
