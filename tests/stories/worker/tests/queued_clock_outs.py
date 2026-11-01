from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.queued_worker import QueuedWorker

TEST_SCRIPT = "#!/bin/sh\ncase \"$*\" in *passing*) echo '1 passed'; exit 0;; *) echo '1 failed'; exit 1;; esac\n"


@story(QueuedWorker, subject=AgentRole.WORKER)
@setting(WorkersOptions.TEST_COMMAND, "./run_tests.sh")
def test_a_worker_with_a_task_queued_is_handed_it_as_it_proves_the_last_point_and_clocks_out_once_its_queue_is_done_with_the_tests_run(story):
    story.project_script_holding("run_tests.sh", TEST_SCRIPT)
    story.agent_proves(story.agents.subject, 1, "parser.py:12, test_reads passes")
    result = story.agent_proves(story.agents.subject, 2, "parser.py:30, test_names passes")
    result.expect_command_text(f"your next task, {story.tasks.queued}")
    result.expect_agent_not_told(story.agents.main, WorkersNudges.WORK_READY)
    story.agent_proves(story.agents.subject, 1, "docs.md:4, the docs name the parser")
    result = story.agent_runs(story.agents.subject, "clock-out 'the queue is done' --tests failing_story.py")
    result.expect_command_refused()
    result.expect_command_text("your tests did not pass")
    result = story.agent_runs(story.agents.subject, "clock-out 'the queue is done' --tests passing_story.py")
    result.expect_command_passed()
    result.expect_agent_told(story.agents.main, WorkersNudges.WORK_READY)
    story.expect_stack(story.agents.subject, Void)


@story(QueuedWorker, subject=AgentRole.WORKER)
def test_a_worker_with_a_task_still_queued_may_not_clock_out(story):
    story.agent_proves(story.agents.subject, 1, "parser.py:12, test_reads passes")
    result = story.agent_runs(story.agents.subject, "clock-out 'the parser is half done'")
    result.expect_command_refused()
    result.expect_command_text(f"its last proof hands you task {story.tasks.queued}")
    story.expect_stack(story.agents.subject, Void, WorkingTask)
