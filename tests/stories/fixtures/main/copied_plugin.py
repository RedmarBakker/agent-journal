from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.installed_plugin import ECHO
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class CopiedPlugin(StateFixture):
    """The user installed the echo plugin from a copy in a folder of their own, so its files may be changed: story.plugins.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.plugins.first = "echo"
        story.user_types(f"plugin install {story.plugin_folder_copied(ECHO)} --yes")

    def expected(self, story) -> None:
        story.last_step.expect_command_text(f"installed {self.plugins.first}, on")
