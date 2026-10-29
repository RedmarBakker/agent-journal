from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.working_agent import WorkingAgent

RESEARCHER = "journal-researcher"


class StartedSubagent(StateFixture):
    """The agent sent a researcher subagent and it started, working on a stack of its own while the agent's stays as it was: story.agents.subagent."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.subagents.first = "agent-first"
        story.agent_sends_subagent(story.agents.main, RESEARCHER, "find where the parser is called")
        story.subagent_starts(self.subagents.first, RESEARCHER)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.subagent, Void, Researching)
        story.expect_stack(story.agents.main, Ready)
