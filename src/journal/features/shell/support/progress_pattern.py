import re

from journal.support.rejection import Rejection

# what may stand between a group and the words that say what it counts: spaces and the quantifiers on them
SPACING = re.compile(r"(?:\\s|\\ | )[*+?]?|^[*+?]")
PERCENT_SIGNS = ("%", "\\%")
COUNT_JOINS = {"/", "\\/", "of", "outof"}


class ProgressPattern:
    """A reader's progress pattern checked for the shape Progress reads it by: one group is a percentage, so the % must follow it, and two are a count of a total, so / or of must join them; any other shape is refused with the reason."""

    @classmethod
    def checked(cls, pattern: str, owner: str) -> None:
        groups = cls.groups(pattern)
        if len(groups) == 1 and not cls.unspaced(pattern[groups[0][1]:]).startswith(PERCENT_SIGNS):
            raise Rejection(f"{owner}'s pattern {pattern!r} has one group and no % after it: add %, or use (\\d+)/(\\d+)")
        if len(groups) == 2 and SPACING.sub("", pattern[groups[0][1]:groups[1][0]]) not in COUNT_JOINS:
            raise Rejection(f"{owner}'s pattern {pattern!r} has two groups not joined by / or of, as in (\\d+)/(\\d+)")
        if len(groups) not in (1, 2):
            raise Rejection(f"{owner}'s pattern {pattern!r} has {len(groups)} groups: one for a percent, or two for a count")

    @staticmethod
    def unspaced(text: str) -> str:
        while (spacing := SPACING.match(text)) and spacing.end():
            text = text[spacing.end():]
        return text

    @staticmethod
    def groups(pattern: str) -> list[tuple[int, int]]:
        opened, spans, index, bracketed = [], [], 0, False
        while index < len(pattern):
            character = pattern[index]
            if character == "\\":
                index += 2
                continue
            if bracketed:
                bracketed = character != "]"
            elif character == "[":
                bracketed = True
            elif character == "(":
                opened.append((index, not pattern.startswith("(?", index) or pattern.startswith(("(?P<", "(?<"), index) and not pattern.startswith(("(?<=", "(?<!"), index)))
            elif character == ")" and opened:
                start, capturing = opened.pop()
                if capturing:
                    spans.append((start, index + 1))
            index += 1
        return sorted(spans)
