from journal.config import Config
from journal.engine.support.lazy_facts import LazyFacts
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.models.agent import Agent
from journal.repositories.messages import Messages
from journal.features.messages.support.peer_question import PeerQuestion
from journal.features.messages.support.turn_replies import TurnReplies
from journal.models.message import Message

# how many unread messages an inbox line gives by number; past these it gives their count
INBOX_LINE_IDS = 4


class MessagesDataReader:
    """Reads the messages feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields MessagesData names."""

    def __init__(self, messages: Messages, config: Config, scope: Scope, stages: StageTimes, turn_replies: TurnReplies) -> None:
        self.messages, self.config, self.scope, self.stages, self.turn_replies = messages, config, scope, stages, turn_replies

    def read(self, agent: Agent) -> LazyFacts:
        facts = LazyFacts("messages", {

            "unread_count": self.messages.unread_count,
            "unread": lambda: tuple(self.messages.unread_page_ids(INBOX_LINE_IDS)),
            "unanswered": lambda: tuple(self.messages.unanswered_ids()),
            "unanswered_files": lambda: tuple(f"{self.config.files / 'message' / str(n)}/" for n in facts.unanswered),
            "peer_questions": lambda: tuple(PeerQuestion(m.row_id, m.data[Message.PEER]) for m in self.messages.peer_questions()),
            "turn_replies": lambda: tuple(m.row_id for m in self.turn_replies.replies(agent.session)),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts
