import re

from journal.engine.nudge import Nudge
from journal.engine.nudge_registry import NudgeRegistry
from journal.engine.nudger import NUDGE
from journal.repositories.entries import Entries

ESCAPED_BLANK = re.compile(r"\\\{\\\{\w+\\\}\\\}")


def nudge_pattern(nudge: Nudge, **values) -> re.Pattern:
    """A registered nudge's line as a pattern: the values given filled in, every other blank standing for any text."""
    return re.compile(ESCAPED_BLANK.sub(".+?", re.escape(nudge.create(**values).rendered())))


def has_nudge(text: str, nudge: Nudge, **values) -> bool:
    """Whether the text the agent was sent holds the nudge's line, found by the nudge as registered, never by its words."""
    return nudge_pattern(nudge, **values).search(text) is not None


def nudge_reached(app, text: str, nudge: Nudge, **values) -> bool:
    """Whether the nudger sent the registered nudge with these values, by its entry, and its line is in the text the agent was sent."""
    app.container.get(NudgeRegistry).lookup(nudge.key)
    wanted = {name: str(value) for name, value in values.items()}
    sent = [entry.data["line"] for entry in app.container.get(Entries).all() if entry.kind == NUDGE and entry.data.get("key") == nudge.key and wanted.items() <= entry.data.get("values", {}).items()]
    return any(line in text for line in sent)
