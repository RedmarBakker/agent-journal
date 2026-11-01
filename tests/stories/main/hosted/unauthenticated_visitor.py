from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_visitor_without_a_login_is_sent_to_the_hosted_login_before_the_viewer(story):
    result = story.hosted_visitor_opens("/journal/manifest")
    result.expect_hosted_login_required()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_visitor_without_a_login_cannot_read_an_api_route(story):
    result = story.hosted_visitor_opens("/journal/messages")
    result.expect_hosted_login_required()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_wrong_hosted_password_leaves_the_visitor_outside_the_journal(story):
    result = story.hosted_visitor_submits_password("wrong password")
    result.expect_hosted_login_rejected()
    result = story.hosted_visitor_opens("/journal/plans")
    result.expect_hosted_login_required()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_correct_hosted_password_opens_the_journal_through_a_private_session(story):
    result = story.hosted_visitor_opens("/login")
    result.expect_hosted_login_form()
    result = story.hosted_visitor_submits_password("story hosted password 123")
    result.expect_hosted_session_created()
    result = story.hosted_visitor_opens("/journal/health")
    result.expect_hosted_journal_reached()
    story.expect_stack(story.agents.subject, Ready)
