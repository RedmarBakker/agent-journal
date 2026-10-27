import re

from journal.engine.nudge import Nudge

ESCAPED_BLANK = re.compile(r"\\\{\\\{\w+\\\}\\\}")


def nudge_pattern(nudge: Nudge, **values) -> re.Pattern:
    """A registered nudge's line as a pattern: the values given filled in, every other blank standing for any text."""
    return re.compile(ESCAPED_BLANK.sub(".+?", re.escape(nudge.create(**values).rendered())))


def has_nudge(text: str, nudge: Nudge, **values) -> bool:
    """Whether the text the agent was sent holds the nudge's line, found by the nudge as registered, never by its words."""
    return nudge_pattern(nudge, **values).search(text) is not None
