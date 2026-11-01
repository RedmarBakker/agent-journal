from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.two_phase_plan import TwoPhasePlan


@story(TwoPhasePlan, subject=AgentRole.MAIN)
@setting(TasksOptions.AUTO, False)
def test_a_phase_end_with_auto_mode_off_waits_for_the_user(story):
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.first_phase} --how done")
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_told(story.agents.subject, PlansNudges.CHECKPOINT_PHASE_END, n=story.plans.first)
    story.expect_task(story.tasks.second_phase, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(TwoPhasePlan, subject=AgentRole.MAIN)
@setting(TasksOptions.AUTO, True)
def test_a_checkpoint_in_auto_mode_goes_straight_on_to_the_next_phase(story):
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.first_phase} --how done")
    story.expect_task(story.tasks.second_phase, state=TaskState.STARTED)
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
