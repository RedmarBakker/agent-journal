from journal.features.seed import Seed
from journal.features.shell.support.readers import RULES_VERSION, Readers
from journal.support.actor import Actor


class ProjectReadersClear(Seed):
    """At boot after the reader rules changed, the readers the project wrote are removed with the defaults file and the aliases that named them lose their reader, plugin and shipped readers kept, so the agents write fresh readers the suggester guides."""

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def run(self) -> None:
        if self.readers.rules_version() < RULES_VERSION:
            self.readers.rules_updated(Actor.system())
