from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.supervisor_proposal import SupervisorProposal


@story(SupervisorProposal, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_stores_a_proposal_without_running_its_command(story):
    result = story.supervisor_posts("/_supervisor/v1/apply", story.proposal_request)
    result.expect_viewer_passed()
    result.expect_viewer_part(("status",), "proposed")
    result.expect_viewer_part(("data", "command"), story.proposal_command)
    result.expect_viewer_part(("data", "wake_up"), story.proposal_wake_up)
    result.expect_viewer_part(("data", "rationale"), story.proposal_rationale)
    result.expect_viewer_part_is_truthy(("proposal_id",))
    story.expect_row_in(story.supervisor_environment, "plans", story.supervisor_plan, {"priorities": ""})
    story.expect_stack(story.agents.subject)
