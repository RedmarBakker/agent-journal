from journal.support.agent_role import AgentRole
from journal.support.actor import Actor
from journal.supervisor_authority import SUPERVISOR_ACTOR
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_helpers import StoryHelpers
from tests.stories.fixtures.state_fixture import StateFixture


class StoryAgents:
    """The agents a story names as the first argument of a step or a check: its subject, the main agent, fixture workers, reviewers and verifiers, its subagent, and the supervisor."""

    def __init__(self, subject: AgentRole, fixture: StateFixture, supervisor_grant_credential: str = "", supervisor_plugin_credential: str = "") -> None:
        self.main = StoryAgent(AgentRole.MAIN)
        self.workers = StoryHelpers(AgentRole.WORKER, fixture.workers)
        self.reviewers = StoryHelpers(AgentRole.REVIEWER, fixture.reviewers)
        self.verifiers = StoryHelpers(AgentRole.VERIFIER, fixture.verifiers)
        self.subagents = fixture.subagents
        self.supervisor = StoryAgent(AgentRole.SUPERVISOR, actor=Actor.plugin(SUPERVISOR_ACTOR),
                                     credential=supervisor_plugin_credential, grant_credential=supervisor_grant_credential)
        self.subject = {AgentRole.MAIN: lambda: self.main, AgentRole.WORKER: self.workers.first, AgentRole.REVIEWER: self.reviewers.first, AgentRole.VERIFIER: self.verifiers.first, AgentRole.SUBAGENT: lambda: self.subagent, AgentRole.SUPERVISOR: lambda: self.supervisor}[subject]()

    @property
    def subagent(self) -> StoryAgent:
        return StoryAgent(AgentRole.SUBAGENT, 0, self.subagents.row("first", ""))
