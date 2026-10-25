from collections.abc import Callable

from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs


class RunHistory(CommandOutputs):
    """The command runs of the past, read by the reader that watched them, by the folder they ran in after a moment, or by a test each run is put to."""

    def reader_unended(self, reader: str) -> list[CommandOutput]:
        return self.selected(self.query().filter(watch_reader=reader, ended=False).order_descending("id"))

    def reader_ended(self, reader: str, last: int) -> list[CommandOutput]:
        return self.selected(self.query().filter(watch_reader=reader, ended=True).order_descending("id").limit(last))

    def latest_accepted(self, count: int, accepts: Callable[[CommandOutput], bool]) -> list[CommandOutput]:
        return [run for run in self.latest(count) if accepts(run)]

    def recent_commands(self, folder: str, moment: float) -> list[str]:
        return [run.command for run in self.ran_within(folder) if run.creation_time.timestamp() >= moment]
