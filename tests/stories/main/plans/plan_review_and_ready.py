from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.draft_plan import DraftPlan


@story(DraftPlan, subject=AgentRole.MAIN)
def test_the_agent_can_neither_ready_a_plan_with_no_phase_nor_approve_it(story):
    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, f"plan approve {story.plans.first}")
    result.expect_command_refused()
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(DraftPlan, subject=AgentRole.MAIN)
def test_a_phase_with_no_task_is_not_ready(story):
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Layout' --when 'the layout stands'")
    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_refused()
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(DraftPlan, subject=AgentRole.MAIN)
def test_a_ready_plan_is_not_started_before_the_user_approves(story):
    grid = story.agent_adds_plan_task(story.agents.subject, story.plans.first, "the grid")
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Layout' --when 'the layout stands'")
    story.agent_runs(story.agents.subject, f"plan todos {story.plans.first} 1 {grid}")
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    story.expect_plan(story.plans.first, state=PlanState.READY)
    result = story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
