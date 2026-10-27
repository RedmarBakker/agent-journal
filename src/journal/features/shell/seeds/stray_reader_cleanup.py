from journal.features.seed import Seed
from journal.features.shell.support.command_mark_policy import CommandMarkPolicy
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.readers import Readers


class StrayReaderCleanup(Seed):
    """At boot, every reader the project kept for searches, reads or git and GitHub commands alone is removed, since those runs get no reader and show no card; a plugin's readers stay with their plugin."""

    def __init__(self, readers: Readers, mark_policy: CommandMarkPolicy) -> None:
        self.readers, self.mark_policy = readers, mark_policy

    def run(self) -> None:
        for reader in self.readers.all():
            if self.is_unwanted(reader):
                self.readers.removed(reader.name)

    def is_unwanted(self, reader: Reader) -> bool:
        return bool(reader.commands.programs) and all(self.mark_policy.takes_no_reader(program) for program in reader.commands.programs) and not self.readers.is_locked(reader.name)
