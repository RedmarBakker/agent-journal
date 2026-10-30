from journal.engine.states.void import Void
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, JOURNAL_TESTING, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.working_worker import WorkingWorker

TEST_SCRIPT = "#!/bin/sh\ncase \"$*\" in *passing*) echo '1 passed'; exit 0;; *) echo '1 failed'; exit 1;; esac\n"


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
@setting(WorkersOptions.TESTING, JOURNAL_TESTING)
@setting(WorkersOptions.TEST_COMMAND, "./run_tests.sh")
def test_a_worker_with_a_task_queued_goes_on_without_a_test_run_or_a_report_and_its_last_clock_out_runs_the_tests_and_reports(story):
    story.project_script_holding("run_tests.sh", TEST_SCRIPT)
    docs = story.agent_creates_task(story.agents.main, "the docs")
    story.agent_runs(story.agents.main, f"worker queue {story.agents.subject} {docs}")
    story.agent_proves(story.agents.subject, 1, "parser.py:12, test_reads passes")
    story.agent_proves(story.agents.subject, 2, "parser.py:30, test_names passes")
    result = story.agent_runs(story.agents.subject, "clock-out 'the parser is done' --tests failing_story.py")
    result.expect_command_passed()
    result.expect_command_text("your next task")
    result.expect_agent_not_told(story.agents.main, WorkersNudges.WORK_READY)
    story.agent_proves(story.agents.subject, 1, "docs.md:4, the docs name the parser")
    result = story.agent_runs(story.agents.subject, "clock-out 'the queue is done' --tests failing_story.py")
    result.expect_command_refused()
    result.expect_command_text("your tests did not pass")
    result = story.agent_runs(story.agents.subject, "clock-out 'the queue is done' --tests passing_story.py")
    result.expect_command_passed()
    result.expect_agent_told(story.agents.main, WorkersNudges.WORK_READY)
    story.expect_stack(story.agents.subject, Void)
