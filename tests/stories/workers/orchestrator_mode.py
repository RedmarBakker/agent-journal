from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.delegating import Delegating
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.orchestrator_with_open_task import OrchestratorWithOpenTask
from tests.stories.fixtures.working_agent import WorkingAgent


@story(WorkingAgent, end=[Orchestrating])
def test_switching_to_orchestrator_mode_names_the_mode_at_the_next_tool(story):
    story.user_sets(WorkersOptions.MODE, ORCHESTRATOR_MODE)
    story.agent_reads()
    story.expect_agent_told(WorkersNudges.ORCHESTRATOR_MODE)
    story.expect_stack(Orchestrating)


@story(OrchestratorWithOpenTask, end=[Orchestrating])
def test_an_orchestrator_stop_with_an_open_task_names_it_to_dispatch(story):
    story.agent_stops()
    story.expect_agent_told(WorkersNudges.ORCHESTRATE, count=1)


@story(OrchestratorWithOpenTask, end=[Orchestrating, Delegating])
def test_an_orchestrator_that_takes_a_task_in_hand_is_told_to_delegate_it(story):
    story.agent_runs(f"task start {story.start.briefed}")
    story.agent_writes("parser.py")
    story.expect_agent_told(WorkersNudges.TASK_DELEGATION)
    story.expect_stack(Orchestrating, Delegating)


@story(OrchestratorWithOpenTask, end=[Orchestrating])
@setting(WorkersOptions.ORCHESTRATOR_RELEASES, False)
def test_an_orchestrator_release_is_refused_while_the_user_has_not_allowed_it(story):
    story.agent_runs_in_the_shell("git tag v9.9.9")
    story.expect_refused(WorkersNudges.RELEASE_REFUSED)


@story(OrchestratorWithOpenTask, end=[Orchestrating])
@setting(WorkersOptions.ORCHESTRATOR_WRITES_PLANS, False)
def test_an_orchestrator_may_not_write_a_plan_while_the_user_has_not_allowed_it(story):
    story.agent_runs("plan create 'the parser plan' --brief 'the parser'")
    story.expect_command_refused()


@story(OrchestratorWithOpenTask, end=[Ready])
def test_switching_back_to_builder_mode_leaves_the_orchestrator_state(story):
    story.user_sets(WorkersOptions.MODE, BUILDER_MODE)
    story.agent_reads()
    story.expect_stack(Ready)
