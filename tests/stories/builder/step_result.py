from journal.console.support.outcome import Outcome
from tests.stories.builder.hook_verdict import HookVerdict
from tests.stories.builder.step_checks import StepChecks


class StepResult(StepChecks):
    """What one step of a story brought, returned by the step for the checks made on it."""

    def __init__(self, story, said: tuple, verdict: HookVerdict | None, command: Outcome | None, shell_text: str, shell_exit: int, viewer_status: int, viewer_answer: object) -> None:
        self.story, self.said, self.verdict, self.command = story, said, verdict, command
        self.shell_text, self.shell_exit, self.viewer_status, self.viewer_answer = shell_text, shell_exit, viewer_status, viewer_answer
