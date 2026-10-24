from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.models.author import Author
from journal.models.link import Link
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor


class ReplyTaskLinks(Listener[Created]):
    """A task linked to a user's message is linked to the agent's reply to it too, so the task shows the whole exchange: when the link is made, its message's replies are linked, and when a reply comes, it is linked to every task its message is; never twice."""

    def __init__(self, messages: Messages, links: Links) -> None:
        self.messages, self.links = messages, links

    def handle(self, event: Created) -> None:
        if isinstance(event.model, Link) and event.model.kind == Messages.SUBJECT_LINK and event.model.source.type == Message.table() and event.model.target.type == Task.table():
            self.task_linked(event.model, event.actor)
        if isinstance(event.model, Message) and event.model.author == Author.AGENT and event.model.reply_target:
            self.reply_link(event.model, event.actor)

    def task_linked(self, link: Link, actor: Actor) -> None:
        requested = self.messages.find(link.source.id)
        if requested.author != Author.USER:
            return
        for reply in self.messages.replies(requested):
            self.linked(reply, link.target, actor)

    def reply_link(self, reply: Message, actor: Actor) -> None:
        for task in self.links.typed_targets(self.messages.find(reply.reply_target), Messages.SUBJECT_LINK, Task.table()):
            self.linked(reply, task, actor)

    def linked(self, reply: Message, task: Ref, actor: Actor) -> None:
        if task not in self.links.targets(reply, Messages.SUBJECT_LINK):
            self.links.save(Link(source=Ref.build(reply), target=task, kind=Messages.SUBJECT_LINK), actor)
