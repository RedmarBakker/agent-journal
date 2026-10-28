from journal.features.briefing.briefing_options import BriefingOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask

TASK_LIST = "journal task list"


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(BriefingOptions.OVERVIEW_COMMANDS, [TASK_LIST])
def test_the_overview_runs_the_commands_the_setting_names(story):
    story.agent_looks_at_the_overview()
    story.expect_command_passed()
    story.expect_command_line(TASK_LIST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_default_overview_shows_the_task_in_hand(story):
    story.agent_looks_at_the_overview()
    story.expect_command_line("the footer")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_default_overview_shows_the_followed_plan(story):
    story.agent_looks_at_the_overview()
    story.expect_command_line(f"plan {story.start.plan}")
    story.expect_stack(Ready, FollowingPlan)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(BriefingOptions.OVERVIEW_COMMANDS, [])
def test_an_overview_with_no_commands_still_counts_as_read(story):
    story.agent_looks_at_the_overview()
    story.expect_command_passed()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
