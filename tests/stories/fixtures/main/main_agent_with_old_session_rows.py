from journal.features.tasks.states.ready import Ready
from journal.models.agent import Agent
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class MainAgentWithOldSessionRows(StateFixture):
    """The live main session has older unended sessions in rows with larger IDs."""

    parent = WorkingAgent
    stack = (Ready,)

    def steps(self, story) -> None:
        agents = story.app.container.get(Agents)
        current = agents.session_agent(story.main_session())
        with story.app.container.get(Scope).environment(current.environment_id):
            for session in ("old-main-session-first", "old-main-session-second"):
                agents.save(Agent(
                    environment_id=current.environment_id, session=session, provider=story.provider,
                    state=current.state, data=current.data, stack=current.stack,
                ), Actor.system())
        story.observed("an older journal left unended session rows beside the live main session", None, None)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
