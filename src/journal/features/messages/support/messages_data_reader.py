from journal.config import Config
from journal.engine.support.lazy_facts import LazyFacts
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.models.agent import Agent
from journal.repositories.messages import Messages
from journal.features.messages.support.peer_question import PeerQuestion
from journal.models.message import Message

# how many unread messages an inbox line gives by number; past these it gives their count
INBOX_LINE_IDS = 4


class MessagesDataReader:
    """Reads the messages feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields MessagesData names."""

    def __init__(self, messages: Messages, config: Config, scope: Scope, stages: StageTimes) -> None:
        self.messages, self.config, self.scope, self.stages = messages, config, scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        facts = LazyFacts("messages", {

            "unread_count": self.messages.unread_count,
            "unanswered_rows": self.messages.unanswered,
            "unread": lambda: tuple(self.messages.unread_page_ids(INBOX_LINE_IDS)),
            "unanswered": lambda: tuple(m.row_id for m in facts.unanswered_rows),
            "unanswered_files": lambda: tuple(f"{self.config.files / 'message' / str(m.id)}/" for m in facts.unanswered_rows),
            "peer_questions": lambda: tuple(PeerQuestion(m.row_id, m.data[Message.PEER]) for m in self.messages.peer_questions()),
            "unread_comments": lambda: tuple(m.row_id for m in self.messages.unread_comments()),
            "tool_use_reads": lambda: tuple(m.row_id for m in facts.unanswered_rows if m.read_at and m.read_position == agent.tool_uses),
            "unlinked_message": lambda: agent.unlinked_message,
            "unlinked_numbers": lambda: agent.unlinked_numbers,
            "missing_message": lambda: wrong.row_id if (wrong := self.messages.missing_rows_message(agent.session)) else 0,
            "missing_rows": lambda: tuple(wrong.data[Message.MISSING_ROWS]) if (wrong := self.messages.missing_rows_message(agent.session)) else (),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts
