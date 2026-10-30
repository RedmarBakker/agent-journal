from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.manual_draft_plan import ManualDraftPlan
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

REVIEWER = "a7"


@story(ManualDraftPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_in_review_is_neither_approved_nor_ready_again_until_its_reviewer_is_back_and_the_round_is_kept_with_its_reviewer_report_and_change(story):
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Lay the floor'")
    task = story.agent_creates_task(story.agents.subject, "pour the slab")
    story.agent_runs(story.agents.subject, f"plan todos {story.plans.first} 1 {task}")
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    story.agent_runs(story.agents.subject, f"plan review {story.plans.first}")
    story.expect_command_passed()
    story.user_presses(f"/journal/plans/{story.plans.first}/approve", {})
    story.expect_viewer_refused("is in review")
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, f"review plan {story.plans.first}", REVIEWER)
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    story.expect_command_refused()
    story.expect_command_text("1 reviewers still out")
    story.subagent_ends(REVIEWER)
    story.expect_plan(story.plans.first, reviewers=0)
    story.agent_runs(story.agents.subject, f"report create 'Plan review' --abstract 'two gaps' --body 'two gaps' --about plans:{story.plans.first}")
    report = story.created_number("report")
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    story.expect_command_refused()
    story.expect_command_text("--changed")
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first} --changed 'the slab task reworded'")
    story.expect_command_passed()
    story.user_opens(f"/journal/plans?ids={story.plans.first}")
    story.expect_viewer_part(("rows", 0, "reviews", 0, "reviewers"), [f"review plan {story.plans.first}"])
    story.expect_viewer_part(("rows", 0, "reviews", 0, "changed"), "the slab task reworded")
    story.expect_viewer_part(("rows", 0, "reviews", 0, "report_ids"), [report])
    story.user_approves_plan(story.plans.first)
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_stack(story.agents.subject, Ready)
