from journal.support.command_shape import CommandShape

SHOWN_CHARACTERS = 100
ELLIPSIS = "…"


class CommandText:
    """A command as the viewer shows it: only its first line, so a heredoc shows its command and not its text, as the command shape shows it, with a subshell's brackets, a folder change before it, the variables set before it and a time limit around it left out, and cut to a set length, or to a given length on a whole word."""

    @staticmethod
    def shown(part: str) -> str:
        first_line = CommandText.first_line(part)
        return first_line if len(first_line) <= SHOWN_CHARACTERS else first_line[:SHOWN_CHARACTERS - 1].rstrip() + ELLIPSIS

    @staticmethod
    def shortened(part: str, characters: int) -> str:
        first_line = CommandText.first_line(part)
        return first_line if len(first_line) <= characters else first_line[:characters - 1].rsplit(" ", 1)[0].rstrip() + ELLIPSIS

    @staticmethod
    def first_line(part: str) -> str:
        return CommandShape.shown(part.strip().split("\n", 1)[0])
