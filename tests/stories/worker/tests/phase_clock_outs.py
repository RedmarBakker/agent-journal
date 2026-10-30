from journal.engine.states.void import Void
from journal.features.workers.workers_options import BUILDER_MODE, JOURNAL_TESTING, WorkersOptions
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.plan_worker import PlanWorker

TEST_SCRIPT = "#!/bin/sh\ncase \"$*\" in *passing*) echo '1 passed'; exit 0;; *) echo '1 failed'; exit 1;; esac\n"


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
@setting(WorkersOptions.TESTING, JOURNAL_TESTING)
@setting(WorkersOptions.TEST_COMMAND, "./run_tests.sh")
def test_a_worker_clocks_out_mid_phase_with_its_tests_still_failing_and_only_the_phase_s_last_task_needs_them_to_pass(story):
    story.project_script_holding("run_tests.sh", TEST_SCRIPT)
    story.agent_proves(story.agents.subject, 1, "first.py:3, the story written first")
    result = story.agent_runs(story.agents.subject, "clock-out 'the stories are written and fail as they should' --tests failing_story.py")
    result.expect_command_passed()
    story.agent_proves(story.agents.subject, 1, "second.py:3, the code that makes the story pass")
    result = story.agent_runs(story.agents.subject, "clock-out 'the plan is done' --tests failing_story.py")
    result.expect_command_refused()
    result.expect_command_text("your tests did not pass")
    result = story.agent_runs(story.agents.subject, "clock-out 'the plan is done' --tests passing_story.py")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Void)
