from journal.features.client_errors.client_errors_nudges import ClientErrorsNudges
from journal.features.client_errors.client_errors_options import ClientErrorsOptions
from journal.features.faults.faults_options import FaultsOptions
from journal.features.client_errors.support.client_errors_data_reader import REMINDER_TOOL_USES
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.viewer_console_error import ERROR, STACK, ViewerConsoleError
from tests.stories.fixtures.main.working_agent import WorkingAgent

ONE_ERROR = ClientErrorsNudges.errors(1)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(ClientErrorsOptions.REPORT, False)
def test_with_the_setting_off_the_agent_hears_nothing_of_the_viewers_errors(story):
    story.viewer_logs_a_console_error("y is null", "at Bar.vue:3")
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, ClientErrorsNudges.LOGGED)
    result.expect_agent_not_told(story.agents.subject, ClientErrorsNudges.UNHANDLED)
    story.expect_stack(story.agents.subject, Ready)


@story(ViewerConsoleError, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_same_viewer_error_again_is_counted_and_not_told(story):
    result = story.viewer_logs_a_console_error(ERROR, STACK)
    result.expect_agent_not_told(story.agents.subject, ClientErrorsNudges.LOGGED)
    result = story.agent_runs(story.agents.subject, "developer client-errors")
    result.expect_command_line(f"2x {ERROR}")
    result.expect_command_text(STACK)
    story.expect_stack(story.agents.subject, Ready)


@story(ViewerConsoleError, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_unhandled_viewer_error_is_named_again_at_the_reminder_tool_use_and_not_before(story):
    result = story.agent_reads(story.agents.subject, count=REMINDER_TOOL_USES - 1)
    result.expect_agent_not_told(story.agents.subject, ClientErrorsNudges.UNHANDLED)
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_told(story.agents.subject, ClientErrorsNudges.UNHANDLED, errors=ONE_ERROR)
    story.expect_stack(story.agents.subject, Ready)


@story(ViewerConsoleError, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_clearing_the_viewer_errors_ends_the_reminders(story):
    result = story.agent_runs(story.agents.subject, "developer client-errors --clear")
    result.expect_command_text("cleared")
    result = story.agent_reads(story.agents.subject, count=REMINDER_TOOL_USES + 1)
    result.expect_agent_not_told(story.agents.subject, ClientErrorsNudges.UNHANDLED)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(ClientErrorsOptions.REPORT, True)
@setting(FaultsOptions.DEVELOPER, False)
def test_with_the_developer_features_off_the_agent_hears_nothing_of_the_viewers_errors_whatever_their_own_setting(story):
    story.viewer_logs_a_console_error("z is null", "at Baz.vue:5")
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, ClientErrorsNudges.LOGGED)
    story.expect_stack(story.agents.subject, Ready)
