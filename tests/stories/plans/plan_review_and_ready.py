from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.draft_plan import DraftPlan


@story(DraftPlan, end=[Ready, FollowingSequence])
def test_a_plan_with_no_phase_is_not_ready(story):
    story.agent_runs(f"plan ready {story.start.plan}")
    story.expect_command_refused()
    story.expect_plan(story.start.plan, state=PlanState.DRAFT)


@story(DraftPlan, end=[Ready, FollowingSequence])
def test_a_phase_with_no_task_is_not_ready(story):
    story.agent_runs(f"plan phase {story.start.plan} 'Layout' --when 'the layout stands'")
    story.agent_runs(f"plan ready {story.start.plan}")
    story.expect_command_refused()
    story.expect_plan(story.start.plan, state=PlanState.DRAFT)


@story(DraftPlan, end=[Ready, FollowingSequence])
def test_a_ready_plan_is_not_started_before_the_user_approves(story):
    grid = story.agent_adds_plan_task(story.start.plan, "the grid", "- the grid has four columns")
    story.agent_runs(f"plan phase {story.start.plan} 'Layout' --when 'the layout stands'")
    story.agent_runs(f"plan todos {story.start.plan} 1 {grid}")
    story.agent_runs(f"plan ready {story.start.plan}")
    story.expect_plan(story.start.plan, state=PlanState.READY)
    story.agent_runs(f"plan start {story.start.plan}")
    story.expect_command_refused()


@story(DraftPlan, end=[Ready, FollowingSequence])
def test_the_agent_cannot_approve_a_plan(story):
    story.agent_runs(f"plan approve {story.start.plan}")
    story.expect_command_refused()
    story.expect_plan(story.start.plan, state=PlanState.DRAFT)
