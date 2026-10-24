from journal.repositories.messages import Messages
from journal.repositories.setting_rows import SettingRows
from journal.support.announced_commands import AnnouncedCommands
from journal.support.chain import Chain
from journal.features.shell.shell_options import ShellOptions
from journal.support.foreground_option import FOREGROUND_OPTION


class ForegroundLimit:
    """How many seconds a line may run in the foreground before the rest moves to the background: none for a line of journal commands or a command a subagent announced, fewer while the user waits on a message."""

    def __init__(self, settings: SettingRows, messages: Messages, announced: AnnouncedCommands) -> None:
        self.settings, self.messages, self.announced = settings, messages, announced

    def build(self, line: str, environment: str, session: str | None) -> int:
        if Chain.is_journal_line(line) or self.announced.is_announced(environment, session, tuple(Chain.self_parts(line))):
            return 0
        waiting = bool(self.messages.unread())
        return self.settings.integer(ShellOptions.MESSAGE_FOREGROUND_LIMIT if waiting else FOREGROUND_OPTION)
