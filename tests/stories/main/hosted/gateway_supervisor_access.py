from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_gateway_listener_refuses_enrollment_without_a_service_token(story):
    result = story.gateway_listener_posts("/_supervisor/v1/enrollment")
    result.expect_gateway_listener_refused()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_gateway_service_route_still_requires_its_service_token(story):
    result = story.gateway_listener_posts("/_supervisor/v1/admit")
    result.expect_gateway_service_token_required()
    story.expect_stack(story.agents.subject, Ready)
