import re

from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.support.timeout import Timeout
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent.tool_finished import ToolFinished
from journal.events.rows.user_resumed import UserResumed
from journal.events.rows.reaction_added import ReactionAdded
from journal.events.rows.colleague_commented import ColleagueCommented
from journal.support.chain import Chain
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.messages.messages_part import MessagesPart

TRUNCATED = re.compile(r"(?:^|[;&|(]\s*)\S*journal\s+(?:message\s+(?:read|unread|recent)|question\s+(?:show|list))\b[^|;&\"']*\|")


class MessagesConduct(Conduct):
    """The messages feature's conduct in every state: the inbox named at a prompt and a stop and every so many of the agent's own tool uses, a write blocked once the unread were named often enough, the tools blocked while a read message stays unanswered past so many uses and an answer asked for before that, a read of the user's words piped into a filter blocked, the reply tag hinted after a message sent by command, and after a tool use that read a message how to answer it, the user's emoji on a message informed, a colleague's comment informed as no words of the user's, and at a session start the comments that arrived while no agent ran."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        comments = event.data.part(MessagesPart).unread_comments
        return self.none(MessagesNudges.UNREAD_COMMENTS.create(ns=", ".join(map(str, comments)))) if comments else self.none()

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.none(*inbox_line(event.data.part(MessagesPart).unread))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if self.blocks_tools():
            return self.none()
        messages = event.data.part(MessagesPart)
        return self.none(*inbox_line(messages.unread), *[MessagesNudges.PEER_QUESTION.create(sender=q.sender, n=q.message) for q in messages.peer_questions])

    def on_user_resumed(self, event: UserResumed, settings: Settings) -> Transition:
        if event.agent_session != event.session:
            return self.none()
        return self.none(*inbox_line(event.data.part(MessagesPart).unread))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return Transition.merged(self, [truncated_read_check(self, event, settings), unanswered_check(self, event, settings), unread_check(self, event, settings)])

    def on_tool_finished(self, event: ToolFinished, settings: Settings) -> Transition:
        if event.subagent:
            return self.none()
        return self.none(*[MessagesNudges.MESSAGE_READ.create(n=n) for n in event.data.part(MessagesPart).tool_use_reads])

    def on_colleague_commented(self, event: ColleagueCommented, settings: Settings) -> Transition:
        return self.none(MessagesNudges.COLLEAGUE_COMMENT.create(colleague=event.colleague, n=event.row_id))

    def on_reaction_added(self, event: ReactionAdded, settings: Settings) -> Transition:
        return self.none(MessagesNudges.USER_REACTION.create(emoji=event.emoji, n=event.message_id)) if event.user_origin else self.none()



def inbox_line(unread: tuple[int, ...]) -> list[Nudge]:
    return [MessagesNudges.inbox(unread)] if unread else []


def file_reads(event: ToolStarting, folders: tuple[str, ...]) -> bool:
    return any(path.startswith(folder) for path in event.call.read_paths for folder in folders)


def truncated_read_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    return state.refuse(MessagesNudges.FULL_MESSAGE_READ.create()) if TRUNCATED.search(event.call.command) else state.none()


def unanswered_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    messages = event.data.part(MessagesPart)
    if event.subagent or not messages.unanswered or event.call.is_journal or file_reads(event, messages.unanswered_files):
        return state.none()
    obligations = ", ".join(str(n) for n in messages.unanswered)
    if Timeout.tool_uses(settings.integer(MessagesOptions.TOOL_BLOCK_LIMIT)).is_elapsed(messages.uses_unanswered):
        return state.refuse(MessagesNudges.UNANSWERED_TOOL_BLOCK.create(messages=obligations))
    if Timeout.tool_uses(settings.integer(MessagesOptions.ANSWER_REQUEST_LIMIT)).is_elapsed(messages.uses_unanswered):
        return state.none(MessagesNudges.unanswered_countdown(messages.unanswered, settings.integer(MessagesOptions.TOOL_BLOCK_LIMIT) - messages.uses_unanswered - 1))
    return state.none()


def unread_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    messages = event.data.part(MessagesPart)
    if event.subagent or event.call.is_journal or not messages.unread:
        return state.none()
    limit = settings.integer(MessagesOptions.EDIT_BLOCK_LIMIT)
    if event.call.writes and Timeout.tool_uses(limit).is_elapsed(messages.inbox_tool_uses):
        return state.refuse(MessagesNudges.INBOX_EDIT_BLOCK.create(count=len(messages.unread)))
    return state.none(MessagesNudges.inbox_countdown(messages.unread, max(limit - messages.inbox_tool_uses - 1, 0)))
