from journal.features.seed import Seed
from journal.features.shell.support.readers import Readers


class JournalOutputReaders(Seed):
    """At boot, every reader the project kept for a journal command's output is removed, since the journal writes and shows that output whole itself (an alias's run of a program is the program's output and keeps its reader); a plugin's readers stay with their plugin."""

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def run(self) -> None:
        for reader in self.readers.journal_readers():
            self.readers.removed(reader.name)
