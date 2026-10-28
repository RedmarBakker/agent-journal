from journal.features.faults.faults_options import FaultsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

TASKS_ROUTE = "/journal/tasks"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_with_the_developer_features_off_nothing_is_timed(story):
    story.user_opens(TASKS_ROUTE)
    story.agent_runs("developer slowest")
    story.expect_command_passed()
    story.expect_command_text("nothing logged yet")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FaultsOptions.DEVELOPER, True)
def test_with_the_load_count_off_no_record_is_counted(story):
    story.user_opens(TASKS_ROUTE)
    story.agent_runs("developer loads")
    story.expect_command_text("nothing counted")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FaultsOptions.DEVELOPER, True)
def test_the_viewers_requests_are_listed_and_a_reset_clears_them(story):
    story.user_opens(TASKS_ROUTE)
    story.agent_runs("developer slowest")
    story.expect_command_text(TASKS_ROUTE)
    story.agent_runs("developer reset")
    story.expect_command_passed()
    story.agent_runs("developer slowest")
    story.expect_command_text("nothing logged yet")
    story.expect_stack(Ready)
