from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.features.tasks.tasks_options import TasksOptions
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.two_phase_plan import TwoPhasePlan


@story(TwoPhasePlan, end=[Ready, FollowingPlan])
@setting(TasksOptions.AUTO, False)
def test_completing_a_phase_completes_every_open_task_of_it_and_no_other(story):
    story.agent_runs(f"plan complete-phase {story.start.plan} 1 --how 'the layout stands'")
    story.expect_command_passed()
    story.expect_task(story.start.first_phase_task, state=TaskState.COMPLETED)
    story.expect_task(story.start.second_phase_task, state=TaskState.OPEN)


@story(TwoPhasePlan, end=[Ready, FollowingPlan])
def test_cancelling_a_phase_cancels_every_open_task_of_it_and_no_other(story):
    story.agent_runs(f"plan cancel-phase {story.start.plan} 2 --why 'the content moves to another plan'")
    story.expect_command_passed()
    story.expect_task(story.start.second_phase_task, state=TaskState.CANCELLED)
    story.expect_task(story.start.first_phase_task, state=TaskState.STARTED)


@story(TwoPhasePlan, end=[Ready, FollowingPlan])
def test_a_phase_the_plan_does_not_have_is_refused(story):
    story.agent_runs(f"plan complete-phase {story.start.plan} 3 --how 'nothing'")
    story.expect_command_refused()
    story.expect_task(story.start.first_phase_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_phase_task, state=TaskState.OPEN)
