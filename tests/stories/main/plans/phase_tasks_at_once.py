from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.two_phase_plan import TwoPhasePlan


@story(TwoPhasePlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(TasksOptions.AUTO, False)
def test_completing_a_phase_completes_every_open_task_of_it_and_no_other(story):
    result = story.agent_runs(story.agents.subject, f"plan complete-phase {story.plans.first} 1 --how 'the layout stands'")
    result.expect_command_passed()
    story.expect_task(story.tasks.first_phase, state=TaskState.COMPLETED)
    story.expect_task(story.tasks.second_phase, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(TwoPhasePlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_cancelling_a_phase_cancels_every_open_task_of_it_and_no_other(story):
    result = story.agent_runs(story.agents.subject, f"plan cancel-phase {story.plans.first} 2 --why 'the content moves to another plan'")
    result.expect_command_passed()
    story.expect_task(story.tasks.second_phase, state=TaskState.CANCELLED)
    story.expect_task(story.tasks.first_phase, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(TwoPhasePlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_phase_the_plan_does_not_have_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"plan complete-phase {story.plans.first} 3 --how 'nothing'")
    result.expect_command_refused()
    story.expect_task(story.tasks.first_phase, state=TaskState.STARTED)
    story.expect_task(story.tasks.second_phase, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
