from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_proposal_rule import SupervisorProposalRule
from tests.test_supervisor_actions import maintenance_request


@story(SupervisorProposalRule, subject=AgentRole.MAIN)
def test_an_owner_rule_turns_a_supervisor_act_into_a_proposal(story):
    context = story.fixture.context
    plan_id = story.plans.first
    operation = {"kind": "plan_priorities", "plan_id": plan_id, "text": "Review the failed check first"}
    result = story.supervisor_posts("/_supervisor/v1/apply", maintenance_request(context, [operation]))
    result.expect_viewer_passed()
    result.expect_viewer_part(("data", "status"), "proposed")
    result.expect_viewer_part(("data", "reason"), "the owner requires this verb to be proposed")
    story.expect_row_in(
        context["fixture"].owner_environment.name, "plans", plan_id,
        {"priorities": context["fixture"].plan.priorities},
    )
    story.expect_supervisor_grant_stays_with_plan(story.grants.first, plan_id)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)
