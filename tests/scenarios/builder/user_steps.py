import re
import uuid

from journal.support.option import Option
from tests.full_project import MAIN
from tests.in_process import posted


class UserSteps:
    """What the user does in a scenario, each a sentence that posts to the route the viewer's client posts to, as the user's own request."""

    def user_sends_message(self, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "idempotency": uuid.uuid4().hex})["id"]

    def user_creates_plan(self, title: str, brief: str) -> int:
        return self.user_posted("/journal/plans", {"title": title, "brief": brief})["id"]

    def user_adds_plan_task(self, plan: int, title: str) -> int:
        return self.user_posted(f"/journal/plans/{plan}/tasks", {"title": title})["id"]

    def user_approves_plan(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/approve", {})

    def user_pauses_plan(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/pause", {})

    def user_sets(self, option: Option, value: object) -> None:
        top, _, name = option.key.partition(".")
        self.user_posted("/journal/settings", {top: {name: value}}, f"user sets {option.key} to {value}")
        held = self.setting(option)
        assert held == value, f"{option.key} was set to {value!r} in the viewer but the journal holds {held!r}"

    def user_posted(self, path: str, body: dict, action: str = "") -> dict:
        status, answer = posted(self.app, path, body, MAIN)
        assert status < 300, f"the viewer's request {path} was refused: {answer}"
        self.observed(action or f"user posts {re.sub(r'/\d+', '/{n}', path)}", None, None)
        return answer
