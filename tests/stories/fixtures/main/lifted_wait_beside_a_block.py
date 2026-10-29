from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class LiftedWaitBesideABlock(StateFixture):
    """The agent at work blocked the deploy until a check passes, waited on the deploy until another check passes, and lifted the wait with its next tool use: story.tasks.blocked, story.checks.block and story.checks.wait."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.tasks.blocked = story.agent_creates_task(story.agents.main, "deploy")
        story.agent_runs(story.agents.main, f"task block {self.tasks.blocked} 'the deploy' --until false")
        self.checks.block = story.newest("checks")
        story.agent_runs(story.agents.main, "await 'the deploy to finish' --until false")
        self.checks.wait = story.newest("checks")
        story.agent_reads(story.agents.main)

    def expected(self, story) -> None:
        story.expect_row("checks", self.checks.wait, {"wait_target": True})
