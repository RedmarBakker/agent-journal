from journal.support.command_shape import VARIABLE_PATTERN

SHOWN_CHARACTERS = 100
ELLIPSIS = "…"


class CommandText:
    """A command as the viewer shows it: the variables set before it left out, only its first line, so a heredoc shows its command and not its text, and cut to a set length."""

    @staticmethod
    def shown(part: str) -> str:
        first_line = VARIABLE_PATTERN.sub("", part.strip(), count=1).split("\n", 1)[0].strip()
        return first_line if len(first_line) <= SHOWN_CHARACTERS else first_line[:SHOWN_CHARACTERS - 1].rstrip() + ELLIPSIS
