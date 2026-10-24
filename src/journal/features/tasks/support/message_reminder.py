from journal.models.task import Task
from journal.repositories.messages import Messages


class MessageReminder:
    """The line that reminds the agent to link the user's newest message, read since a task last changed, to a task, when no task has it."""

    def __init__(self, messages: Messages) -> None:
        self.messages = messages

    def line(self, task: Task) -> str:
        unfiled = self.messages.unfiled_reads(task.update_time)
        return f"message {unfiled[-1].id} of the user is read and linked to no task: `journal task edit {task.id} --from {unfiled[-1].id}` if this edit comes from it" if unfiled else ""
