from journal.features.shell.support.background_commands import BackgroundCommands
from journal.repositories.messages import Messages
from journal.repositories.setting_rows import SettingRows
from journal.support.announced_commands import AnnouncedCommands
from journal.support.chain import Chain
from journal.features.shell.shell_options import ShellOptions
from journal.support.foreground_option import FOREGROUND_OPTION


class ForegroundLimit:
    """How many seconds a line may run in the foreground before the rest moves to the background: none for a line of journal commands or a command a subagent announced, fewer while the user waits on a message; a journal command its command names among its background verbs, such as worker merge, goes to the background at once."""

    def __init__(self, settings: SettingRows, messages: Messages, announced: AnnouncedCommands, background: BackgroundCommands) -> None:
        self.settings, self.messages, self.announced, self.background = settings, messages, announced, background

    def build(self, line: str, environment: str, session: str | None) -> int:
        if (Chain.is_journal_line(line) and not self.is_background(line)) or self.announced.is_announced(environment, session, tuple(Chain.self_parts(line))):
            return 0
        waiting = self.messages.unread_count() > 0
        return self.settings.integer(ShellOptions.MESSAGE_FOREGROUND_LIMIT if waiting else FOREGROUND_OPTION)

    def is_background(self, line: str) -> bool:
        return self.background.is_background(line)
