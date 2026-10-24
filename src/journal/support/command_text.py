from journal.support.command_shape import CommandShape

SHOWN_CHARACTERS = 100
ELLIPSIS = "…"


class CommandText:
    """A command as the viewer shows it: only its first line, so a heredoc shows its command and not its text, as the command shape shows it, with a subshell's brackets, a folder change before it, the variables set before it and a time limit around it left out, and cut to a set length."""

    @staticmethod
    def shown(part: str) -> str:
        first_line = CommandShape.shown(part.strip().split("\n", 1)[0])
        return first_line if len(first_line) <= SHOWN_CHARACTERS else first_line[:SHOWN_CHARACTERS - 1].rstrip() + ELLIPSIS
