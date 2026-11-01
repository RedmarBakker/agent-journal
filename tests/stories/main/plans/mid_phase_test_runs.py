from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.mid_phase_test_plan import MidPhaseTestPlan
from tests.stories.fixtures.main.started_plan import StartedPlan

FIRST_PHASE = 1


@story(MidPhaseTestPlan, subject=AgentRole.MAIN)
def test_a_test_run_mid_phase_is_refused_with_the_plan_testing_and_how_to_run_it_anyway(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "pytest -q tests/test_parser.py")
    result.expect_refused(story.agents.subject, PlansNudges.MID_PHASE_TESTS, n=story.plans.first, phase=FIRST_PHASE)
    story.expect_task(story.tasks.second, state=TaskState.STARTED)
    story.expect_task(story.tasks.third, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(MidPhaseTestPlan, subject=AgentRole.MAIN)
def test_an_allowance_lets_one_test_run_through_and_the_next_is_refused_again(story):
    story.agent_runs(story.agents.subject, f"plan allow-tests {story.plans.first} --why 'one test of the parser'")
    result = story.agent_runs_in_the_shell(story.agents.subject, "pytest -q tests/test_parser.py")
    result.expect_allowed()
    story.expect_task_logged(story.tasks.second, "one test of the parser")
    result = story.agent_runs_in_the_shell(story.agents.subject, "pytest -q tests/test_parser.py")
    result.expect_refused(story.agents.subject, PlansNudges.MID_PHASE_TESTS, n=story.plans.first, phase=FIRST_PHASE)
    story.expect_task(story.tasks.second, state=TaskState.STARTED)
    story.expect_task(story.tasks.third, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(MidPhaseTestPlan, subject=AgentRole.MAIN)
def test_an_allowance_without_a_reason_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"plan allow-tests {story.plans.first}")
    result.expect_command_refused()
    story.expect_task(story.tasks.second, state=TaskState.STARTED)
    story.expect_task(story.tasks.third, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(MidPhaseTestPlan, subject=AgentRole.MAIN)
def test_a_test_run_on_the_last_task_of_the_phase_goes_through_unasked(story):
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.second} --how 'the about page stands'")
    result = story.agent_runs_in_the_shell(story.agents.subject, "pytest -q tests/test_parser.py")
    result.expect_allowed()
    story.expect_task(story.tasks.third, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(StartedPlan, subject=AgentRole.MAIN)
def test_a_plan_with_no_testing_set_never_refuses_a_test_run(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "pytest -q tests/test_parser.py")
    result.expect_allowed()
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
