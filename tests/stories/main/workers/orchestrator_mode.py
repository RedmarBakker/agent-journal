from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.states.delegating import Delegating
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.orchestrator_open_task import OrchestratorOpenTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
def test_switching_to_orchestrator_mode_names_the_mode(story):
    story.user_sets(WorkersOptions.MODE, ORCHESTRATOR_MODE)
    story.expect_agent_told(WorkersNudges.ORCHESTRATOR_MODE)
    story.agent_reads()
    story.expect_stack(Orchestrating)


@story(OrchestratorOpenTask, mode=ORCHESTRATOR_MODE)
def test_an_orchestrator_stop_with_an_open_task_names_it_to_dispatch(story):
    story.agent_stops()
    story.expect_agent_told(WorkersNudges.ORCHESTRATE, count=1)
    story.expect_stack(Orchestrating)


@story(OrchestratorOpenTask, mode=ORCHESTRATOR_MODE)
def test_an_orchestrator_that_stops_with_a_task_in_hand_is_told_to_delegate_it(story):
    story.agent_runs(f"task start {story.start.briefed}")
    story.agent_stops()
    story.expect_agent_told(WorkersNudges.TASK_DELEGATION)
    story.expect_stack(Orchestrating, Delegating)


@story(OrchestratorOpenTask, mode=ORCHESTRATOR_MODE)
@setting(WorkersOptions.ORCHESTRATOR_RELEASES, False)
def test_an_orchestrator_release_is_refused_while_the_user_has_not_allowed_it(story):
    story.agent_runs_in_the_shell("git tag v9.9.9")
    story.expect_refused(WorkersNudges.RELEASE_REFUSED)
    story.expect_stack(Orchestrating)


@story(OrchestratorOpenTask, mode=ORCHESTRATOR_MODE)
@setting(WorkersOptions.ORCHESTRATOR_WRITES_PLANS, False)
def test_an_orchestrator_may_not_write_a_plan_while_the_user_has_not_allowed_it(story):
    story.agent_runs("plan create 'the parser plan' --brief 'the parser'")
    story.expect_command_refused()
    story.expect_stack(Orchestrating)


@story(OrchestratorOpenTask, mode=ORCHESTRATOR_MODE)
def test_back_in_builder_mode_a_stop_takes_the_open_task_up_instead_of_naming_it_for_dispatch(story):
    story.user_sets(WorkersOptions.MODE, BUILDER_MODE)
    story.agent_stops()
    story.expect_agent_not_told(WorkersNudges.ORCHESTRATE)
    story.expect_task(story.start.briefed, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
