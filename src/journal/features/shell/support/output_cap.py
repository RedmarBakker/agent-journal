from journal.features.shell.support.background_commands import BackgroundCommands
from journal.features.shell.support.cap import Cap, DIRECT, ENDS, HINT, FULL
from journal.repositories.setting_rows import SettingRows
from journal.support.chain import Chain
from journal.support.command_lines import CommandLines
from journal.support.refusal_command import RefusalCommand
from journal.features.shell.shell_options import ShellOptions


class OutputCap:
    """Decides a line's cap from its parts and the Settings page's numbers; a journal command that goes to the background is capped as any other command, so its output is kept under a number."""

    def __init__(self, settings: SettingRows, background: BackgroundCommands, lines: CommandLines) -> None:
        self.settings, self.background, self.lines = settings, background, lines

    def build(self, line: str) -> Cap:
        if self.lines.is_code_read(line) or self.lines.is_code_write(line) or RefusalCommand.is_refusal(line):
            return Cap(DIRECT, 0)
        if Chain.is_journal_line(line) and not self.background.is_background(line):
            return Cap(FULL, 0)
        if self.lines.is_read(line):
            return Cap(ENDS, self.settings.integer(ShellOptions.READ_SHOWN))
        return Cap(HINT, self.settings.integer(ShellOptions.COMMAND_SHOWN))
