from journal.features.client_errors.client_errors_nudges import ClientErrorsNudges
from journal.features.client_errors.client_errors_options import ClientErrorsOptions
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

ERROR, STACK = "x is undefined", "at Chat.vue:12"


class ViewerConsoleError(StateFixture):
    """The user switched on telling the agent about the viewer's errors, and the viewer logged one, told to the agent at once."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.user_sets(ClientErrorsOptions.REPORT, True)
        story.viewer_logs_a_console_error(ERROR, STACK)

    def expected(self, story) -> None:
        story.expect_agent_told(ClientErrorsNudges.LOGGED, errors=ClientErrorsNudges.errors(1))
