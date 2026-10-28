from journal.models.task_state import TaskState
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_removing_the_check_a_task_waits_on_alone_opens_the_task(story):
    release = story.agent_creates_task("ship it")
    story.agent_runs(f"task block {release} 'the build' --until false")
    wait = story.created_number("check")
    story.expect_task(release, state=TaskState.BLOCKED)
    story.agent_runs(f"check remove {wait}")
    story.expect_task(release, state=TaskState.OPEN)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_removed_check_leaves_the_list_and_cannot_be_removed_again(story):
    story.agent_runs("check create 'the build' --command false --every 5 --brief 'the build passes'")
    build = story.created_number("check")
    story.agent_runs(f"check remove {build}")
    story.agent_runs("check list")
    story.expect_command_text_without("the build")
    story.agent_runs(f"check remove {build}")
    story.expect_command_text("removed already")
    story.expect_stack(Ready)
