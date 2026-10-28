from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.mid_phase_test_plan import MidPhaseTestPlan
from tests.stories.fixtures.main.started_plan import StartedPlan

FIRST_PHASE = 1


@story(MidPhaseTestPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_test_run_mid_phase_is_refused_with_the_plan_testing_and_how_to_run_it_anyway(story):
    story.agent_runs_in_the_shell("pytest -q tests/test_parser.py")
    story.expect_refused(PlansNudges.MID_PHASE_TESTS, n=story.start.plan, phase=FIRST_PHASE)
    story.expect_task(story.start.second_task, state=TaskState.STARTED)
    story.expect_task(story.start.third_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)


@story(MidPhaseTestPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_allowance_lets_one_test_run_through_and_the_next_is_refused_again(story):
    story.agent_runs(f"plan allow-tests {story.start.plan} --why 'one test of the parser'")
    story.agent_runs_in_the_shell("pytest -q tests/test_parser.py")
    story.expect_allowed()
    story.expect_task_logged(story.start.second_task, "one test of the parser")
    story.agent_runs_in_the_shell("pytest -q tests/test_parser.py")
    story.expect_refused(PlansNudges.MID_PHASE_TESTS, n=story.start.plan, phase=FIRST_PHASE)
    story.expect_task(story.start.second_task, state=TaskState.STARTED)
    story.expect_task(story.start.third_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)


@story(MidPhaseTestPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_allowance_without_a_reason_is_refused(story):
    story.agent_runs(f"plan allow-tests {story.start.plan}")
    story.expect_command_refused()
    story.expect_task(story.start.second_task, state=TaskState.STARTED)
    story.expect_task(story.start.third_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)


@story(MidPhaseTestPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_test_run_on_the_last_task_of_the_phase_goes_through_unasked(story):
    story.agent_runs(f"task complete {story.start.second_task} --how 'the about page stands'")
    story.agent_runs_in_the_shell("pytest -q tests/test_parser.py")
    story.expect_allowed()
    story.expect_task(story.start.third_task, state=TaskState.STARTED)
    story.expect_stack(Ready, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_with_no_testing_set_never_refuses_a_test_run(story):
    story.agent_runs_in_the_shell("pytest -q tests/test_parser.py")
    story.expect_allowed()
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)
