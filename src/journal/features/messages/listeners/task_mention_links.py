import re
from journal.events.models.created import Created
from journal.events.listener import Listener
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.missing_row import MissingRow
from journal.repositories.tasks import Tasks

TASK_PATTERN = re.compile(r"\btask (\d+)\b", re.IGNORECASE)


class TaskMentionLinks(Listener[Created]):
    """A task the agent's reply names is linked to the message it answers, so the chat shows it above that message."""

    def __init__(self, messages: Messages, tasks: Tasks, links: Links) -> None:
        self.messages, self.tasks, self.links = messages, tasks, links

    def handle(self, event: Created) -> None:
        reply = event.model
        if not isinstance(reply, Message) or not reply.is_agent_message() or not reply.reply_target:
            return
        try:
            requested = self.messages.find(reply.reply_target)
        except MissingRow:
            return
        for n in {int(n) for n in TASK_PATTERN.findall(reply.text)}:
            try:
                task = self.tasks.find(n)
            except MissingRow:
                continue
            self.links.linked(Ref.build(requested), Ref.build(task), Messages.SUBJECT_LINK, event.actor)
