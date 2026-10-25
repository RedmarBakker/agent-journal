import re

# the git commands whose outcome the journal marks in the chat itself, so a line of them alone is given no reader
WRITING_COMMANDS = re.compile(r"^git (commit|push)\b")


class GitWrites:
    """Whether a command is a git commit or a git push, which the journal marks in the chat itself and so never need a reader; every other git step, a rebase among them, may have one."""

    @staticmethod
    def is_writing(command: str) -> bool:
        return bool(WRITING_COMMANDS.match(command.strip()))
