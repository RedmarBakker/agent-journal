from journal.features.shell.support.background_commands import BackgroundCommands
from journal.features.shell.support.cap import Cap, DIRECT, ENDS, HINT, FULL
from journal.repositories.setting_rows import SettingRows
from journal.support.chain import Chain
from journal.support.refusal_command import RefusalCommand
from journal.support.writes import Writes
from journal.features.shell.shell_options import ShellOptions


class OutputCap:
    """Decides a line's cap from its parts and the Settings page's numbers; a journal command that goes to the background is capped as any other command, so its output is kept under a number."""

    def __init__(self, settings: SettingRows, background: BackgroundCommands) -> None:
        self.settings, self.background = settings, background

    def build(self, line: str) -> Cap:
        if Chain.is_reading_code_line(line) or Writes.is_code_write_line(line) or RefusalCommand.is_refusal(line):
            return Cap(DIRECT, 0)
        if Chain.is_journal_line(line) and not self.background.is_background(line):
            return Cap(FULL, 0)
        if Chain.is_read_line(line):
            return Cap(ENDS, self.settings.integer(ShellOptions.READ_SHOWN))
        return Cap(HINT, self.settings.integer(ShellOptions.COMMAND_SHOWN))
