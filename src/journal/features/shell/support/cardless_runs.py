from journal.features.shell.support.activity_label import ActivityLabel, READ_LABELS
from journal.features.shell.support.git_commands import GitCommands
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs

# a read whose same command took this long before shows its card, neutral, while it runs
LONG_READ_SECONDS = 30
# a command none of whose kept runs went past this many seconds was never a background process, and its mark goes at boot
SHORT_RUN_SECONDS = 5


class CardlessRuns:
    """The runs that show no card of their own in the chat and are given no reader: a line that only reads, searches or lists, unless the same command took long before, and a line of git or GitHub commands alone, whose commit and push marks say it; either shows its card once it failed. A mark written before these rules is stray when its run was a git line, failed or not, never moved to the background, cardless, or of a command that never ran past SHORT_RUN_SECONDS."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def is_cardless(self, output: CommandOutput) -> bool:
        if output.ended and not output.is_success():
            return False
        return GitCommands.is_git_line(output.command) or self.is_quick_read(output.command)

    def is_quick_read(self, line: str) -> bool:
        if not ActivityLabel.is_reading(line):
            return False
        last = self.outputs.last_run(line)
        return last is None or last.run_seconds() < LONG_READ_SECONDS

    def is_stray_mark(self, output: CommandOutput) -> bool:
        return GitCommands.is_git_line(output.command) or not output.moved or self.is_cardless(output) or self.outputs.longest_run_seconds(output.command) < SHORT_RUN_SECONDS

    @staticmethod
    def is_cardless_program(command: str) -> bool:
        return GitCommands.is_git(command) or ActivityLabel.build(command) in READ_LABELS
