from journal.models.entry import Entry
from journal.models.message import Message
from journal.references import events
from journal.repositories.entries import Entries
from journal.repositories.messages import Messages


class TurnReplies:
    """The replies the agent sent by command in its turn in hand: the prompt that opened the turn and the replies since it, read the same by the recording of its words and by the line that names words written after a reply."""

    def __init__(self, messages: Messages, entries: Entries) -> None:
        self.messages, self.entries = messages, entries

    def turn_prompt(self, session: str) -> Entry | None:
        prompts = self.entries.session_kind_entries(events.PROMPT_SUBMITTED, session)
        return prompts[0] if prompts else None

    def replies(self, session: str) -> tuple[Message, ...]:
        prompt = self.turn_prompt(session)
        return tuple(self.messages.recent_replies(prompt.creation_time)) if prompt else ()

    def has_reply(self, session: str) -> bool:
        return bool(self.replies(session))
