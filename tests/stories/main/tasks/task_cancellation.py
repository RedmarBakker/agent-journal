from journal.models.task_state import TaskState
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_given_up_without_why_is_refused_and_stays_open(story):
    avatar = story.agent_creates_task("the shared avatar")
    story.agent_runs(f"task cancel {avatar}")
    story.expect_command_refused()
    story.expect_task(avatar, state=TaskState.OPEN)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_given_up_with_why_is_cancelled_with_it_and_leaves_the_list(story):
    avatar = story.agent_creates_task("the shared avatar")
    story.agent_runs(f"task cancel {avatar} --why 'screens differ in size'")
    story.expect_command_text(f"task {avatar} cancelled")
    story.expect_task(avatar, state=TaskState.CANCELLED, outcome="screens differ in size")
    story.agent_runs("task list")
    story.expect_command_text_without("the shared avatar")
    story.expect_stack(Ready)
