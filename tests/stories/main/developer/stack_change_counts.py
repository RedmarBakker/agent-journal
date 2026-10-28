from journal.features.faults.faults_options import FaultsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask

TASK_START_CAUSE = "task_started"


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FaultsOptions.DEVELOPER, True)
def test_the_task_start_is_counted_as_a_kind_of_stack_change_and_with_no_story_run_nothing_is_marked(story):
    story.agent_runs("developer transitions")
    story.expect_command_passed()
    story.expect_command_text(TASK_START_CAUSE)
    story.expect_command_text("no full scenario run has written")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FaultsOptions.DEVELOPER, True)
def test_a_kind_the_last_story_run_did_not_walk_is_marked(story):
    story.story_run_walked("no state > idle on session_started")
    story.agent_runs("developer transitions")
    story.expect_command_text("no story walks it")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
