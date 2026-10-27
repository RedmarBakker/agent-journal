from pathlib import Path

from journal.features.shell.support.activity_label import LONG_RUNS, ActivityLabel
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.silent_run import SilentRun
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.support.time_source import TimeSource

# how long a background run may print nothing before the agent is told its command holds its output back
SILENCE_SECONDS = 20


class SilentRuns:
    """The agent's background test runs and builds that have printed nothing at all for SILENCE_SECONDS or more since they began: a buffered command, never a run that is only slow between its lines, nor a command that prints nothing by its nature, such as a sleep."""

    def __init__(self, outputs: CommandOutputs, time_source: TimeSource, labels: ActivityLabel) -> None:
        self.labels = labels
        self.outputs, self.time_source = outputs, time_source

    def running(self, session: str) -> tuple[SilentRun, ...]:
        current_seconds, moved_outputs = self.time_source.seconds(), self.outputs.background(session)
        return tuple(SilentRun(output.row_id, output.command, int(current_seconds - output.creation_time.timestamp())) for output in moved_outputs if self.is_silent(output, current_seconds))

    def is_silent(self, output: CommandOutput, current_seconds: float) -> bool:
        return self.labels.line_label(output.command) in LONG_RUNS and OutputFiles(Path(output.folder)).size() == 0 and current_seconds - output.creation_time.timestamp() >= SILENCE_SECONDS
