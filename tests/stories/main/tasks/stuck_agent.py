from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.agent_impasse import AgentImpasse
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_stuck_with_tasks_open_is_refused(story):
    story.agent_creates_task("the header")
    story.agent_runs_in_the_shell("journal stuck 'the build fails'")
    story.expect_refused(TasksNudges.IMPASSE_REFUSAL)
    story.expect_stack(Ready)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_in_hand_counts_as_work_left(story):
    story.agent_runs_in_the_shell("journal stuck 'the build fails'")
    story.expect_refused(TasksNudges.IMPASSE_REFUSAL, count=1)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(AgentImpasse, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_agents_next_tool_use_ends_the_stuck_state(story):
    story.agent_reads()
    story.expect_allowed()
    story.expect_stack(Ready)


@story(AgentImpasse, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_journal_command_keeps_the_agent_stuck(story):
    story.agent_runs_in_the_shell("journal task list")
    story.expect_stack(Ready, Impasse)


@story(AgentImpasse, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_users_prompt_ends_the_stuck_state(story):
    story.agent_is_prompted("try the build again")
    story.expect_stack(Ready)


@story(AgentImpasse, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_stop_while_stuck_goes_through(story):
    story.agent_stops()
    story.expect_allowed()
    story.expect_stack(Ready, Impasse)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_agent_stuck_on_its_task_in_hand_waits_over_it_until_its_next_tool_use(story):
    story.agent_runs("stuck 'the build fails on the footer'")
    story.expect_stack(Ready, Working, Impasse)
    story.agent_reads()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
