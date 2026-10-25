from journal.features.shell.support.activity_label import ActivityLabel, READ_LABELS
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.support.chain import Chain
from journal.support.command_shape import CommandShape

# the everyday git a line may do and still show no card, since the journal's commit and push marks say it; a rebase or a history
# rewrite is not among them
GIT_ROUTINE_LABELS = frozenset({"committing", "pushing", "pulling", "staging", "switching branch", "tagging", "checking git", "fetching", "merging", "reading history", "reading a diff", "listing", "searching"})
# a read whose same command took this long before shows its card, neutral, while it runs
LONG_READ_SECONDS = 30


class CardlessRuns:
    """The runs that show no card of their own in the chat: a line that only reads, searches or lists, unless the same command took long before, and a line of everyday git, whose commit and push marks say it; either shows its card once it failed."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def is_cardless(self, output: CommandOutput) -> bool:
        if output.ended and not output.is_success():
            return False
        return self.is_git_routine(output.command) or self.is_quick_read(output.command)

    def is_quick_read(self, line: str) -> bool:
        if not ActivityLabel.is_reading(line):
            return False
        last = self.outputs.last_run(line)
        return last is None or last.run_seconds() < LONG_READ_SECONDS

    @staticmethod
    def is_git_routine(line: str) -> bool:
        parts = [part.text for part in Chain.parts(line)]
        return bool(parts) and all(CommandShape.command_name(part).startswith("git") and ActivityLabel.build(part) in GIT_ROUTINE_LABELS for part in parts)
