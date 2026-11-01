from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_logging_in_removes_expired_hosted_sessions(story):
    result = story.hosted_visitor_submits_password("story hosted password 123")
    result.expect_hosted_session_created()

    story.hosted_visitor_waits_for_session_expiration()
    result = story.hosted_visitor_submits_password("story hosted password 123")
    result.expect_hosted_session_created()
    story.expect_hosted_session_count(1)
    story.expect_stack(story.agents.subject, Ready)
