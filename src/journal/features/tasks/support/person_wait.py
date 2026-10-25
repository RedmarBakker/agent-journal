import re

from journal.models.task import Task
from journal.repositories.tasks import Tasks
from journal.repositories.users import Users

# a reason in words that names the user, someone or an outside party, which no command can check
PERSON_WORDS = re.compile(r"\b(users?|someone|somebody|colleagues?|decisions?|decide|repl(y|ies)|answers?|approv\w*|sign-?off|customers?|clients?|vendors?|providers?|third party)\b", re.IGNORECASE)


class PersonWait:
    """Whether a blocked or paused task waits on a person: no --on or --until opens it, and its reason names the user, someone, an outside party, or a person the journal knows by name."""

    def __init__(self, tasks: Tasks, users: Users) -> None:
        self.tasks, self.users = tasks, users

    def is_on_a_person(self, task: Task) -> bool:
        return not self.tasks.open_waits(task) and self.names_a_person(task.waiting_reason())

    def names_a_person(self, reason: str) -> bool:
        names = [word for user in self.users.all() for word in user.name.split()[:1] if len(word) > 1]
        return bool(PERSON_WORDS.search(reason)) or any(re.search(rf"\b{re.escape(name)}\b", reason, re.IGNORECASE) for name in names)
