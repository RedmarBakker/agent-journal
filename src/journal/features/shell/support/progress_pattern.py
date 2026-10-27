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
        if len(groups) == 1 and not cls.bare(pattern[groups[0][1]:]).startswith(PERCENT_SIGNS):
            raise Rejection(f"{owner}'s progress pattern {pattern!r} has one group, which is read as a percentage, but no % follows it: a running count or a time would draw past 100 percent. Follow the group with %, or give two groups, a count and its total, such as (\\d+)/(\\d+)")
        if len(groups) == 2 and SPACING.sub("", pattern[groups[0][1]:groups[1][0]]) not in COUNT_JOINS:
            raise Rejection(f"{owner}'s progress pattern {pattern!r} has two groups, which are read as a count and its total, but no / or of joins them: two numbers that are not a count of a total draw nonsense such as 55/121632227066. Join them with / or of")
        if len(groups) not in (1, 2):
            raise Rejection(f"{owner}'s progress pattern {pattern!r} has {len(groups)} groups: give one for a percentage, followed by %, or two for a count of a total, joined by / or of")

    @staticmethod
    def bare(text: str) -> str:
        while (spacing := SPACING.match(text)) and spacing.end():
            text = text[spacing.end():]
        return text

    @staticmethod
    def groups(pattern: str) -> list[tuple[int, int]]:
        opened, spans, index, in_class = [], [], 0, False
        while index < len(pattern):
            character = pattern[index]
            if character == "\\":
                index += 2
                continue
            if in_class:
                in_class = character != "]"
            elif character == "[":
                in_class = True
            elif character == "(":
                opened.append((index, not pattern.startswith("(?", index) or pattern.startswith(("(?P<", "(?<"), index) and not pattern.startswith(("(?<=", "(?<!"), index)))
            elif character == ")" and opened:
                start, capturing = opened.pop()
                if capturing:
                    spans.append((start, index + 1))
            index += 1
        return sorted(spans)
