from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_helpers import StoryHelpers
from tests.stories.fixtures.state_fixture import StateFixture


class StoryAgents:
    """The agents a story names as the first argument of a step or a check, always written out: its subject, the agent the story is about and its folder names, the main agent, the workers, reviewers and verifiers its fixture made, and the subagent it started."""

    def __init__(self, subject: AgentRole, fixture: StateFixture) -> None:
        self.main = StoryAgent(AgentRole.MAIN)
        self.workers = StoryHelpers(AgentRole.WORKER, fixture.workers)
        self.reviewers = StoryHelpers(AgentRole.REVIEWER, fixture.reviewers)
        self.verifiers = StoryHelpers(AgentRole.VERIFIER, fixture.verifiers)
        self.subagents = fixture.subagents
        self.subject = {AgentRole.MAIN: lambda: self.main, AgentRole.WORKER: self.workers.first, AgentRole.REVIEWER: self.reviewers.first, AgentRole.VERIFIER: self.verifiers.first, AgentRole.SUBAGENT: lambda: self.subagent}[subject]()

    @property
    def subagent(self) -> StoryAgent:
        return StoryAgent(AgentRole.SUBAGENT, 0, self.subagents.row("first", ""))
