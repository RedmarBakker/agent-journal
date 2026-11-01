from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.two_phase_plan import TwoPhasePlan


@story(TwoPhasePlan, subject=AgentRole.MAIN)
def test_a_plan_working_in_its_second_phase_with_a_first_phase_task_blocked_is_in_its_second_phase(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.first_phase} 'the grid waits for the designs'")
    story.agent_runs(story.agents.subject, f"task start {story.tasks.second_phase}")
    result = story.agent_runs(story.agents.subject, f"plan show {story.plans.first}")
    result.expect_command_text("phase in hand: 2 of 2, Content")
    story.expect_task(story.tasks.first_phase, state=TaskState.BLOCKED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(TwoPhasePlan, subject=AgentRole.MAIN)
def test_a_plan_with_no_task_in_progress_is_in_its_earliest_phase_with_open_work(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.first_phase} 'the grid waits for the designs'")
    result = story.agent_runs(story.agents.subject, f"plan show {story.plans.first}")
    result.expect_command_text("phase in hand: 1 of 2, Layout")
    story.expect_task(story.tasks.second_phase, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
