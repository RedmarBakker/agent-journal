from pathlib import Path

from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

ECHO = Path(__file__).parents[3] / "plugins" / "echo"


class InstalledPlugin(StateFixture):
    """The user installed the echo plugin from its folder, on: start.plugin."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.plugin = "echo"
        story.user_types(f"plugin install {ECHO} --yes")

    def expected(self, story) -> None:
        story.expect_command_text(f"installed {self.plugin}, on")
