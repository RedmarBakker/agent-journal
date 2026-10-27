from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.features.shell.shell_nudges import ShellNudges
from journal.repositories.reader_suggestions import ReaderSuggestions
from journal.support.actor import Actor


class ReaderSuggestionRecord(AgentListener[LineDelivered]):
    """A reader suggested for a part is recorded for the project with the moment it was said, so the part is not suggested again until its runs come round."""

    def __init__(self, suggestions: ReaderSuggestions) -> None:
        self.suggestions = suggestions

    def handle(self, event: LineDelivered) -> None:
        if event.nudge == ShellNudges.READER_DRAFT.key:
            self.suggestions.suggested(event.values["part"], event.time, Actor.system())
