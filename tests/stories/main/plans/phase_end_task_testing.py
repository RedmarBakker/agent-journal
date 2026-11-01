from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.phase_waiting_for_tests import PhaseWaitingForTests


@story(PhaseWaitingForTests, subject=AgentRole.MAIN)
def test_a_passing_phase_end_test_run_completes_every_task_of_the_phase_waiting_in_testing(story):
    story.recorded_run_ends(story.outputs.first)
    story.expect_task(story.tasks.second, state=TaskState.COMPLETED)
    story.expect_task(story.tasks.third, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)


@story(PhaseWaitingForTests, subject=AgentRole.MAIN)
def test_a_failing_phase_end_test_run_blocks_every_task_waiting_in_testing(story):
    story.recorded_run_fails(story.outputs.first)
    story.expect_task(story.tasks.second, state=TaskState.BLOCKED)
    story.expect_task(story.tasks.third, state=TaskState.BLOCKED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
