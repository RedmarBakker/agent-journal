from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_verb_the_workers_file_does_not_name_is_refused_naming_the_file_and_its_verbs(story):
    story.agent_runs("panic pop")
    story.expect_command_refused()
    story.expect_command_text("a worker may not run journal panic apply: WorkerHelper names the verbs it runs")
    story.expect_command_text("journal memory list")
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_verb_the_workers_file_names_runs_and_its_neighbour_stays_refused(story):
    story.agent_runs("memory list")
    story.expect_command_passed()
    story.agent_runs("rule strike 1")
    story.expect_command_text("a worker may not run journal rule strike")
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_the_help_shows_a_worker_only_the_nouns_and_verbs_it_may_run(story):
    story.agent_runs("-h")
    story.expect_command_text("worker")
    story.expect_command_text_without("panic")
    story.agent_runs("task -h")
    story.expect_command_text("show")
    story.expect_command_text_without("complete")
    story.agent_runs("task")
    story.expect_command_refused()
    story.expect_command_text("{log,show}")
    story.expect_stack(Void, WorkingTask)
