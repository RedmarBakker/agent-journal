import shlex

from journal.features.registry import Registry
from journal.repositories.messages import Messages
from journal.repositories.setting_rows import SettingRows
from journal.support.announced_commands import AnnouncedCommands
from journal.support.chain import Chain
from journal.features.shell.shell_options import ShellOptions
from journal.support.foreground_option import FOREGROUND_OPTION

JOURNAL = "journal"


class ForegroundLimit:
    """How many seconds a line may run in the foreground before the rest moves to the background: none for a line of journal commands or a command a subagent announced, fewer while the user waits on a message; a journal command its command names among its background verbs, such as worker merge, goes to the background at once."""

    def __init__(self, settings: SettingRows, messages: Messages, announced: AnnouncedCommands, registry: Registry) -> None:
        self.settings, self.messages, self.announced, self.registry = settings, messages, announced, registry

    def build(self, line: str, environment: str, session: str | None) -> int:
        if (Chain.is_journal_line(line) and not self.is_background(line)) or self.announced.is_announced(environment, session, tuple(Chain.self_parts(line))):
            return 0
        waiting = self.messages.unread_count() > 0
        return self.settings.integer(ShellOptions.MESSAGE_FOREGROUND_LIMIT if waiting else FOREGROUND_OPTION)

    def is_background(self, line: str) -> bool:
        return any(self.is_background_command(arguments[1:]) for part in Chain.self_parts(line) if (arguments := shlex.split(part))[:1] == [JOURNAL])

    def is_background_command(self, arguments: list[str]) -> bool:
        verb = arguments[2:3] if arguments[1:2] and arguments[1].isdigit() else arguments[1:2]
        return bool(arguments) and bool(verb) and self.registry.is_background_verb(arguments[0], verb[0])
