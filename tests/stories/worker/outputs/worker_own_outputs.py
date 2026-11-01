from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_may_list_its_outputs(story):
    result = story.agent_runs(story.agents.subject, "output list")
    result.expect_command_passed()
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_stopping_with_its_own_output_running_is_refused_with_its_number(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "sleep 2")
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, WorkersNudges.OUTPUT_UNFINISHED, n=output)
    story.background_run_ends(story.agents.subject, output)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
