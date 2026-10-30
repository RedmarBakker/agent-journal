from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_verb_the_workers_file_does_not_name_is_refused_naming_the_file_and_its_verbs(story):
    result = story.agent_runs(story.agents.subject, "panic pop")
    result.expect_command_refused()
    result.expect_command_text("a worker may not run journal panic apply: WorkerHelper names the verbs it runs")
    result.expect_command_text("journal memory list")
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_verb_the_workers_file_names_runs_and_its_neighbour_stays_refused(story):
    result = story.agent_runs(story.agents.subject, "memory list")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "rule strike 1")
    result.expect_command_text("a worker may not run journal rule strike")
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_the_help_shows_a_worker_only_the_nouns_and_verbs_it_may_run(story):
    result = story.agent_runs(story.agents.subject, "-h")
    result.expect_command_text("worker")
    result.expect_command_text_without("panic")
    result = story.agent_runs(story.agents.subject, "task -h")
    result.expect_command_text("show")
    result.expect_command_text_without("complete")
    result = story.agent_runs(story.agents.subject, "task")
    result.expect_command_refused()
    result.expect_command_text("{log,show}")
    story.expect_stack(story.agents.subject, Void, WorkingTask)
