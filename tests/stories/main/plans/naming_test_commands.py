from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.naming_test_commands import NamingTestCommands
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.test_command_wait import TestCommandWait


@story(TestCommandWait, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_with_no_test_commands_holds_writes_until_they_are_named(story):
    result = story.agent_writes(story.agents.subject, "a.py")
    result.expect_refused(story.agents.subject, PlansNudges.TEST_COMMANDS_NEEDED)
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan, NamingTestCommands)


@story(TestCommandWait, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_naming_the_test_commands_lets_the_plan_go_on(story):
    story.user_sets(PlansOptions.TEST_COMMANDS, "journal suite")
    result = story.agent_writes(story.agents.subject, "a.py")
    result.expect_allowed()
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
