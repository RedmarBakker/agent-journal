from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.silent_run import SilentRun
from journal.repositories.command_outputs import CommandOutputs
from journal.support.time_source import TimeSource

# how long a background run may print nothing before the agent is told its command holds its output back
QUIET_SECONDS = 20


class SilentRuns:
    """The agent's background runs that have printed no new line for QUIET_SECONDS or more, measured from their files' last write, or from the start of a run that has printed nothing."""

    def __init__(self, outputs: CommandOutputs, time_source: TimeSource) -> None:
        self.outputs, self.time_source = outputs, time_source

    def running(self, session: str) -> tuple[SilentRun, ...]:
        now = self.time_source.seconds()
        quiet = [(output, now - (OutputFiles(Path(output.folder)).last_write_seconds() or output.creation_time.timestamp())) for output in self.outputs.background(session)]
        return tuple(SilentRun(output.row_id, output.command, int(seconds)) for output, seconds in quiet if seconds >= QUIET_SECONDS)
