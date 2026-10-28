from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.plan_of_two_phases import PlanOfTwoPhases


@story(PlanOfTwoPhases, end=[Ready, FollowingPlan])
@setting(TasksOptions.AUTO, False)
def test_a_phase_end_with_auto_mode_off_waits_for_the_user(story):
    story.agent_runs(f"task complete {story.start.first_phase_task} --how done")
    story.agent_stops()
    story.expect_agent_told(PlansNudges.CHECKPOINT_PHASE_END, n=story.start.plan)
    story.expect_task(story.start.second_phase_task, state=TaskState.OPEN)


@story(PlanOfTwoPhases, end=[Ready, FollowingPlan])
@setting(TasksOptions.AUTO, True)
def test_a_checkpoint_in_auto_mode_goes_straight_on_to_the_next_phase(story):
    story.agent_runs(f"task complete {story.start.first_phase_task} --how done")
    story.expect_task(story.start.second_phase_task, state=TaskState.STARTED)
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
