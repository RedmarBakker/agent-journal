from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_logging_out_ends_the_hosted_session(story):
    result = story.hosted_visitor_submits_password("story hosted password 123")
    result.expect_hosted_session_created()
    result = story.hosted_visitor_logs_out()
    result.expect_hosted_session_removed()
    result = story.hosted_visitor_opens("/journal/health")
    result.expect_hosted_login_required()
    story.expect_stack(story.agents.subject, Ready)
