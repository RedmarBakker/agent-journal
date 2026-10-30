from journal.config import Config

JOURNAL_HOOK_SCRIPT = "src/journal/hooks/hook.sh"


class JournalRepository:
    """Whether the project is the journal's own repository, told by the hook script's source in it."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def is_open(self) -> bool:
        return (self.config.root / JOURNAL_HOOK_SCRIPT).is_file()
