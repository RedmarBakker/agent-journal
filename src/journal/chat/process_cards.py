from journal.chat.card_detail import CardDetail
from journal.chat.card_category import CardCategory
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.author import Author
from journal.models.message import Message
from journal.support.message_thread import MessageThread
from journal.repositories.agents import Agents
from journal.repositories.messages import Messages
from journal.support.answer_phase import AnswerPhase

PROCESS = "process"
DOCKED = "docked"
PINNED = "pinned"
# the progress of a watched card that the agent last saw, kept through a refresh
LAST_PROGRESS_KEY = "last_progress"
DOCK_TIME_KEY = "dock_at"
UNDOCK_TIME_KEY = "undock_at"
# the mark a card takes when the process it shows ran and ended, done or failed: from then on it is never written again
FINAL = "final"


class ProcessCards:
    """Writes every process card: one message per process, found again by its key and updated in place, found and written in one transaction so two shows of one card at once never make two, its data naming the process card class that refreshes it and whether its process still runs; a card whose process ran and ended, done or failed, is final and never written again but by a reader written anew reading its still kept output."""

    def __init__(self, messages: Messages, agents: Agents, phase: AnswerPhase) -> None:
        self.messages, self.agents, self.phase = messages, agents, phase

    def show(self, contents: ProcessCardContents) -> Message:
        with self.messages.writing():
            older = self.messages.keyed(contents.key, contents.actor)
            if older and older[0].data.get(FINAL):
                return older[0]
            return self.save_card(contents, older)

    def reread(self, contents: ProcessCardContents) -> Message:
        with self.messages.writing():
            return self.save_card(contents, self.messages.keyed(contents.key, contents.actor))

    def save_card(self, contents: ProcessCardContents, older: list[Message]) -> Message:
        self.phase.record_viewer_write(type(self).__name__)
        data = {"row": "", **contents.data, **CardDetail.parts(contents.detail), **CardCategory.read(contents.label).fields(), "key": contents.key, "shows": str(contents.shows), "card_type": PROCESS, "process": contents.process, "active": contents.active}
        if older:
            open_card = older[0].data.get("active") or older[0].data.get(FINAL)
            ended = {FINAL: True} if open_card and not contents.active else {}
            return self.messages.save(older[0].with_(text=contents.label, session=contents.session or older[0].session, data={**self.docked_data(older[0], data), **ended}), contents.actor)
        roles = self.agents.session_roles(contents.session) if contents.session else []
        return self.messages.save(Message(environment_id=contents.environment_id, author=Author.SYSTEM, session=contents.session or None, thread=MessageThread.agent_thread(roles[0]) if roles else MessageThread.MAIN, text=contents.label, data=data), contents.actor)

    def is_shown(self, contents: ProcessCardContents) -> bool:
        return bool(self.messages.keyed(contents.key, contents.actor))

    def is_unchanged(self, contents: ProcessCardContents) -> bool:
        older = self.messages.keyed(contents.key, contents.actor)
        return bool(older) and older[0].text == contents.label and all(older[0].data.get(name) == value for name, value in CardDetail.parts(contents.detail).items())

    def show_recent(self, contents: ProcessCardContents) -> Message:
        older = self.messages.keyed(contents.key, contents.actor)
        if older and self.predates_user_message(older[0]):
            self.messages.delete(older[0], contents.actor)
        return self.show(contents)

    def predates_user_message(self, card: Message) -> bool:
        latest = self.messages.last_user_message()
        return latest is not None and card.row_id < latest.row_id

    @staticmethod
    def docked_data(older: Message, data: dict) -> dict:
        return {**{key: older.data[key] for key in (DOCKED, PINNED, DOCK_TIME_KEY, LAST_PROGRESS_KEY) if key in older.data}, **data}
