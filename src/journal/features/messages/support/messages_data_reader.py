from journal.config import Config
from journal.engine.support.lazy_facts import LazyFacts
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.models.agent import Agent
from journal.repositories.messages import Messages
from journal.features.messages.support.peer_question import PeerQuestion
from journal.models.message import Message


class MessagesDataReader:
    """Reads the messages feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields MessagesData names."""

    def __init__(self, messages: Messages, config: Config, scope: Scope, stages: StageTimes) -> None:
        self.messages, self.config, self.scope, self.stages = messages, config, scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        facts = LazyFacts("messages", {
            "unread_rows": self.messages.unread,
            "unanswered_rows": self.messages.unanswered,
            "unread": lambda: tuple(m.row_id for m in facts.unread_rows),
            "unanswered": lambda: tuple(m.row_id for m in facts.unanswered_rows),
            "unanswered_files": lambda: tuple(f"{self.config.files / 'message' / str(m.id)}/" for m in facts.unanswered_rows),
            "inbox_tool_uses": lambda: agent.tool_uses - agent.inbox_position if facts.unread_rows and self.messages.last_user_message() else 0,
            "uses_unanswered": lambda: self.uses_unanswered(agent, facts.unanswered_rows),
            "peer_questions": lambda: tuple(PeerQuestion(m.row_id, m.data[Message.PEER]) for m in self.messages.peer_questions()),
            "unread_comments": lambda: tuple(m.row_id for m in self.messages.unread_comments()),
            "tool_use_reads": lambda: tuple(m.row_id for m in facts.unanswered_rows if m.read_at and m.read_position == agent.tool_uses),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts

    @staticmethod
    def uses_unanswered(agent: Agent, unanswered: list[Message]) -> int:
        read_positions = [m.read_position for m in unanswered if m.read_at]
        return agent.tool_uses - min(read_positions) if read_positions else 0
