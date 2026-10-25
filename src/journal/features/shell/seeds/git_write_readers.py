from journal.features.seed import Seed
from journal.features.shell.support.readers import Readers


class GitWriteReaders(Seed):
    """At boot, every reader the project kept for git commit or git push alone is removed, since those lines show no card and the journal's commit and push marks say them; a plugin's readers stay with their plugin."""

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def run(self) -> None:
        for reader in self.readers.git_write_readers():
            self.readers.removed(reader.name)
