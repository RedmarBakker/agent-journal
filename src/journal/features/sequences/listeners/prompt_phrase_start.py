from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent_listener import AgentListener
from journal.features.sequences.support.phrase_starts import PhraseStarts


class PromptPhraseStart(AgentListener[PromptSubmitted]):
    """The user's own prompt that is a sequence's phrase starts that sequence, before the agent goes on."""

    blocking = True

    def __init__(self, starts: PhraseStarts) -> None:
        self.starts = starts

    def handle(self, event: PromptSubmitted) -> None:
        if event.is_users:
            self.starts.start(event.prompt, event.session, event.environment_id)
