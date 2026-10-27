import threading

from journal.engine.nudge import Nudge
from journal.engine.nudger import Nudger
from journal.engine.support.session_agents import SessionAgents
from journal.events.agent.turn_displayed import TurnDisplayed
from journal.events.agent_listener import AgentListener
from journal.features.messages.support.reaction_emoji import ReactionEmoji
from journal.features.messages.support.tags import Tags
from journal.features.messages.support.word_overlap import WordOverlap
from journal.features.registry import Registry
from journal.support.actor import Actor
from journal.models.author import Author
from journal.models.entry import Entry
from journal.models.message import Message
from journal.support.voice_key import VoiceKey
from journal.providers.providers import Providers
from journal.repositories.entries import Entries
from journal.repositories.messages import Messages
from journal.supervisor_link import SupervisorLink
from journal.features.messages.messages_nudges import MessagesNudges
from journal.references import events

JOURNAL_LINE = "[journal] "
SHORT_CHARACTERS = 240
REPEAT_OVERLAP_RATIO = 0.6



class RecordTurn(AgentListener[TurnDisplayed]):
    """Every whole turn the agent writes for the user becomes a message in the chat, any old command tag stripped from it and run by nothing. A turn that is only a reaction is not posted: the agent is instructed to react. A turn that only answered a journal line and changed nothing is stored as an acknowledgement, out of the chat, but never while the user has paused the agent, when every word it writes is for the user."""

    def __init__(self, messages: Messages, entries: Entries, providers: Providers, registry: Registry, supervisor: SupervisorLink, nudger: Nudger, sessions: SessionAgents) -> None:
        self.messages, self.entries, self.providers, self.registry, self.supervisor = messages, entries, providers, registry, supervisor
        self.nudger, self.sessions = nudger, sessions
        self.recording = threading.Lock()  # the same block arrives at once from the transcript and from the display hook

    def handle(self, event: TurnDisplayed) -> None:
        if not event.final or not event.text.strip():
            return
        if ReactionEmoji.is_emoji(event.text):
            self.typed(event, MessagesNudges.EMOJI_REPLY.create(emoji=event.text.strip()))
            return
        with self.recording:
            self._record(event)

    def typed(self, event: TurnDisplayed, nudge: Nudge) -> None:
        line = self.nudger.deliver(self.sessions.agent(event.session, event.environment_id), nudge)
        if line:
            self.supervisor.type(event.environment_id, line)

    def _record(self, event: TurnDisplayed) -> None:
        actor, text = Actor.agent(event.session), Tags.visible(event.text)
        if text != event.text.strip():
            self.typed(event, MessagesNudges.RETIRED_TAGS.create())
        key = VoiceKey.create("turn", event.session, text)
        if not text or self.messages.sent_with(key) or self.is_repeat_reply(text, event):
            return
        acknowledgement = len(text) <= SHORT_CHARACTERS and "?" not in text and self._journal_answer(event)
        self.messages.save(Message(author=Author.AGENT, text=text, acknowledgement=acknowledgement, idempotency=key), actor)

    def is_repeat_reply(self, text: str, event: TurnDisplayed) -> bool:
        prompt = self.turn_prompt(event)
        if prompt is None:
            return False
        repeated = WordOverlap.repeats(text, self.messages.recent_replies(prompt.creation_time), REPEAT_OVERLAP_RATIO)
        if repeated:
            self.typed(event, MessagesNudges.REPEATED_CLOSING_TEXT.create(reply=repeated[0].id, n=repeated[0].reply_target))
        return bool(repeated)

    def turn_prompt(self, event: TurnDisplayed) -> Entry | None:
        prompts = self.entries.session_kind_entries(events.PROMPT_SUBMITTED, event.session)
        return prompts[0] if prompts else None

    def _journal_answer(self, event: TurnDisplayed) -> bool:
        entry = self.turn_prompt(event)
        if entry is None or self.sessions.blocks_tools(event.session):
            return False
        prompt = entry.data.get("prompt", "")
        if not prompt.startswith(JOURNAL_LINE) or self._chat_answer(event, prompt[len(JOURNAL_LINE):]):
            return False
        provider = self.providers.lookup(event.provider)
        start = self.entries.recent(entry.row_id)
        return not any(e.entry_type == events.TOOL_STARTING and e.is_write() for e in start)

    def _chat_answer(self, event: TurnDisplayed, line: str) -> bool:
        line_text = self.entries.line_entries(event.session, line)
        nudge = self.registry.nudge_keyed(line_text[-1].data["key"]) if line_text else None
        return bool(nudge and nudge.chat_answerable)
