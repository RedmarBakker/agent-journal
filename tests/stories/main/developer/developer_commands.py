from journal.features.faults.faults_options import FaultsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

MESSAGES_ROUTE = "/journal/messages"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(FaultsOptions.DEVELOPER, True)
def test_the_developer_commands_list_the_slowest_routes_drill_into_one_and_reset_them(story):
    story.user_opens(MESSAGES_ROUTE)
    story.user_opens(MESSAGES_ROUTE)
    result = story.agent_runs(story.agents.subject, "developer slowest")
    result.expect_command_text(f"GET {MESSAGES_ROUTE}")
    result = story.agent_runs(story.agents.subject, f"developer inspect 'GET {MESSAGES_ROUTE}'")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "developer inspect 'GET /nowhere'")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, "developer averages")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "developer reset")
    result.expect_command_text("cleared")
    result = story.agent_runs(story.agents.subject, "developer slowest")
    result.expect_command_text("nothing logged yet")
    story.expect_stack(story.agents.subject, Ready)
