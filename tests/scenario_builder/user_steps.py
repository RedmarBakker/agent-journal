import shlex

from journal.support.option import Option
from tests.full_project import USER
from tests.user_settings import user_set


class UserSteps:
    """What the user does in a scenario, each a sentence that runs the command or the viewer request the user would."""

    def user_runs(self, line: str) -> None:
        self.ran(self.app.console().run(shlex.split(line), USER))

    def user_sends_message(self, text: str) -> int:
        sent = self.app.console().run(["message", "send", text], USER)
        self.ran(sent)
        return int(sent.text.split()[1])

    def user_sets(self, option: Option, value: object) -> None:
        user_set(self.app, option.key, value)
        self.observed(None, None)
