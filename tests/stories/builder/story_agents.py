from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_helpers import StoryHelpers
from tests.stories.fixtures.state_fixture import StateFixture


class StoryAgents:
    """The agents a story names as the first argument of a step or a check, always written out: its subject, the agent the story is about and its folder names, the main agent, the workers, reviewers and verifiers its fixture made, and the subagent."""

    def __init__(self, scope: AgentRole, fixture: StateFixture) -> None:
        self.main = StoryAgent(AgentRole.MAIN)
        self.workers = StoryHelpers(AgentRole.WORKER, getattr(fixture, "worker", 0))
        self.reviewers = StoryHelpers(AgentRole.REVIEWER, getattr(fixture, "reviewer", 0))
        self.verifiers = StoryHelpers(AgentRole.VERIFIER, getattr(fixture, "verifier", 0))
        self.subagent = StoryAgent(AgentRole.SUBAGENT, 0)
        self.subject = {AgentRole.MAIN: self.main, AgentRole.WORKER: self.workers.first(), AgentRole.REVIEWER: self.reviewers.first(), AgentRole.VERIFIER: self.verifiers.first(), AgentRole.SUBAGENT: self.subagent}[scope]
