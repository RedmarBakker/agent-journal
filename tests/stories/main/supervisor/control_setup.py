from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_not_set_up import SupervisorNotSetUp


@story(SupervisorNotSetUp, subject=AgentRole.MAIN)
def test_an_owner_sees_setup_when_the_environment_has_no_supervisor(story):
    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "never_set_up")
    result.expect_viewer_part(("grant",), None)

    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/records?period=today")
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "never_set_up")

    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/history")
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "never_set_up")

    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/costs")
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "never_set_up")
    result.expect_viewer_part(("daily_cost_cap_microusd",), None)

    plans = story.user_opens_in(story.supervisor_owner_environment, f"/journal/plans/{story.plans.first}")
    plans.expect_viewer_passed()
    story.expect_stack(story.agents.subject, Ready)
