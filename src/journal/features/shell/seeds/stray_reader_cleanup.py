from journal.features.seed import Seed
from journal.features.shell.support.readers import Readers


class StrayReaderCleanup(Seed):
    """At boot, every reader the project kept for searches, reads or git and GitHub commands alone is removed, since those runs get no reader and show no card; a plugin's readers stay with their plugin."""

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def run(self) -> None:
        for reader in self.readers.stray_readers():
            self.readers.removed(reader.name)
