from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_environment_observation import SupervisorEnvironmentObservation


@story(SupervisorEnvironmentObservation, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_observes_only_the_plans_its_grant_watches(story):
    result = story.supervisor_posts("/_supervisor/v1/observe", story.run_request)
    result.expect_viewer_passed()
    result.expect_viewer_part(("snapshot", "environment", "plan_ids"), [story.plans.first])
    result.expect_viewer_part_is_truthy(("snapshot", "environment_read_id"))
    story.expect_stack(story.agents.subject)
