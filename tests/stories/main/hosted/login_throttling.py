from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from login_throttle import LoginThrottle
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_repeated_wrong_passwords_lock_only_the_forwarded_client(story):
    for attempt in range(LoginThrottle().source_limit):
        if attempt:
            story.hosted_visitor_waits_for_retry()
        forwarded = f"198.51.100.{attempt + 1}, 203.0.113.17"
        result = story.hosted_visitor_submits_password_from("wrong password", forwarded)
        result.expect_hosted_login_rejected()
        result.expect_hosted_login_retry_announced()

    result = story.hosted_visitor_submits_password_from("wrong password", forwarded)
    result.expect_hosted_login_slowed()

    result = story.hosted_visitor_submits_password_from(
        "story hosted password 123", "198.51.100.3, 203.0.113.18"
    )
    result.expect_hosted_session_created()
    story.expect_stack(story.agents.subject, Ready)
