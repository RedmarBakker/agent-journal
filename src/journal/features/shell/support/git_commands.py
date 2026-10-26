import re

from journal.support.chain import Chain
from journal.support.command_shape import CommandShape

# a git or a GitHub command, whose run the journal never reads with a reader nor shows as a card; its commit and push marks say what it did
GIT_COMMAND = re.compile(r"^(git|gh)(\s|$)")


class GitCommands:
    """Whether a command, or every part of a line, is a git or a GitHub command: such a run gets no reader, no watch and no card in the chat, however long it runs."""

    @staticmethod
    def is_git(command: str) -> bool:
        return bool(GIT_COMMAND.match(command.strip()))

    @classmethod
    def is_git_line(cls, line: str) -> bool:
        parts = [part.text for part in Chain.parts(line)]
        return bool(parts) and all(cls.is_git(CommandShape.command_name(part)) for part in parts)
