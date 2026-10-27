import re

from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.message_read import MessageRead
from journal.events.rows.message_rows_faulty import MessageRowsFaulty
from journal.events.rows.user_resumed import UserResumed
from journal.events.rows.reaction_added import ReactionAdded
from journal.events.rows.colleague_commented import ColleagueCommented
from journal.support.chain import Chain
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_part import MessagesPart
from journal.features.messages.support.messages_data import MessagesData

TRUNCATED = re.compile(r"(?:^|[;&|(]\s*)\S*journal\s+(?:message\s+(?:read|unread|recent)|question\s+(?:show|list))\b[^|;&\"']*\|")


class MessagesConduct(Conduct):
    """The messages feature's conduct in every state: the inbox named at a prompt and a stop and every so many of the agent's own tool uses, a read of the user's words piped into a filter blocked, the reply tag hinted after a message sent by command, and after a tool use that read a message how to answer it, the user's emoji on a message informed, a colleague's comment informed as no words of the user's, and at a session start the comments that arrived while no agent ran."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        comments = event.data.part(MessagesPart).unread_comments
        return self.none(MessagesNudges.UNREAD_COMMENTS.create(ns=", ".join(map(str, comments)))) if comments else self.none()

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.none(*inbox_line(event.data.part(MessagesPart)))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if self.blocks_tools():
            return self.none()
        messages = event.data.part(MessagesPart)
        return self.none(*inbox_line(messages), *[MessagesNudges.PEER_QUESTION.create(sender=q.sender, n=q.message) for q in messages.peer_questions])

    def on_user_resumed(self, event: UserResumed, settings: Settings) -> Transition:
        if event.agent_session != event.session:
            return self.none()
        return self.none(*inbox_line(event.data.part(MessagesPart)))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return truncated_read_check(self, event, settings)

    def on_message_rows_faulty(self, event: MessageRowsFaulty, settings: Settings) -> Transition:
        return self.none(*unlinked_line(event), *missing_line(event)) if event.writer_session == event.session else self.none()

    def on_message_read(self, event: MessageRead, settings: Settings) -> Transition:
        return self.none(MessagesNudges.MESSAGE_READ.create(n=event.row_id)) if event.is_agents(event.session) else self.none()

    def on_colleague_commented(self, event: ColleagueCommented, settings: Settings) -> Transition:
        return self.none(MessagesNudges.COLLEAGUE_COMMENT.create(colleague=event.colleague, n=event.row_id))

    def on_reaction_added(self, event: ReactionAdded, settings: Settings) -> Transition:
        return self.none(MessagesNudges.USER_REACTION.create(emoji=event.emoji, n=event.message_id)) if event.user_origin else self.none()



def inbox_line(messages: MessagesData) -> list[Nudge]:
    return [MessagesNudges.inbox(messages.unread, messages.unread_count)] if messages.unread else []


def truncated_read_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    return state.refuse(MessagesNudges.FULL_MESSAGE_READ.create()) if TRUNCATED.search(event.call.command) else state.none()


def unlinked_line(event: MessageRowsFaulty) -> list[Nudge]:
    if not event.unlinked:
        return []
    numbers = ", ".join(f"{row.split()[1]} ({row.split()[0]})" for row in event.unlinked)
    kinds = " ".join(row.split()[0] for row in event.unlinked)
    return [MessagesNudges.UNLINKED_NUMBERS.create(n=event.row_id, numbers=numbers, kinds=kinds)]


def missing_line(event: MessageRowsFaulty) -> list[Nudge]:
    return [MessagesNudges.MISSING_ROWS.create(n=event.row_id, rows=", ".join(event.missing))] if event.missing else []
