from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.messages import Messages


class MessageReminder:
    """The line that reminds the agent to link the user's newest message, read since a task last changed, to a task, when no task has it."""

    def __init__(self, messages: Messages, links: Links) -> None:
        self.messages, self.links = messages, links

    def line(self, task: Task) -> str:
        unlinked = [m for m in self.messages.read_since(task.update_time) if not self.is_linked(m)]
        return f"message {unlinked[-1].id} of the user is read and linked to no task: `journal task edit {task.id} --from {unlinked[-1].id}` if this edit comes from it" if unlinked else ""

    def is_linked(self, message) -> bool:
        return any(ref.type == Task.table() for ref in self.links.targets(message, Messages.SUBJECT_LINK))
