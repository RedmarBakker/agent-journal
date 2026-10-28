import re
import uuid

from journal.support.option import Option
from tests.full_project import MAIN
from tests.in_process import posted


class UserSteps:
    """What the user does in a story, each a sentence that posts to the route the viewer's client posts to, as the user's own request."""

    def user_sends_message(self, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "idempotency": uuid.uuid4().hex})["id"]

    def user_comments_on(self, table: str, row: int, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "on": f"{table}:{row}", "idempotency": uuid.uuid4().hex})["id"]

    def user_answers(self, question: int, answer: str) -> None:
        self.user_posted(f"/journal/questions/{question}/answer", {"answer": answer})

    def user_reacts(self, message: int, emoji: str) -> None:
        self.user_posted(f"/journal/messages/{message}/react", {"emoji": emoji})

    def user_creates_plan(self, title: str, brief: str) -> int:
        return self.user_posted("/journal/plans", {"title": title, "brief": brief})["id"]

    def user_adds_plan_task(self, plan: int, title: str) -> int:
        return self.user_posted(f"/journal/plans/{plan}/tasks", {"title": title, "brief": f"- {title} is done"})["id"]

    def user_approves_plan(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/approve", {})

    def user_pauses_plan(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/pause", {})

    def user_edits_task(self, task: int, title: str) -> None:
        self.user_posted(f"/journal/tasks/{task}", {"title": title}, "user edits a task")

    def user_completes_task(self, task: int, outcome: str) -> None:
        self.user_posted(f"/journal/tasks/{task}/finish", dict(how=outcome), "user completes a task")

    def user_pauses_task(self, task: int, reason: str) -> None:
        self.user_posted(f"/journal/tasks/{task}/pause", dict(why=reason), "user pauses a task")

    def user_cancels_task(self, task: int, reason: str) -> None:
        self.user_posted(f"/journal/tasks/{task}/cancel", dict(why=reason), "user cancels a task")

    def user_sets(self, option: Option, value: object) -> None:
        top, _, name = option.key.partition(".")
        self.user_posted("/journal/settings", {top: {name: value}}, f"user sets {option.key} to {value}")
        stored = self.setting(option)
        assert stored == value, f"{option.key} was set to {value!r} in the viewer but the journal holds {stored!r}"
        self.set_positions[option.key] = self.reads.position()

    def user_posted(self, path: str, body: dict, action: str = "") -> dict:
        status, answer = posted(self.app, path, body, MAIN)
        assert status < 300, f"the viewer's request {path} was refused: {answer}"
        self.observed(action or f"user posts {re.sub(r'/\d+', '/{n}', path)}", None, None)
        return answer
