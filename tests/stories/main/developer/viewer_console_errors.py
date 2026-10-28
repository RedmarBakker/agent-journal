from journal.features.client_errors.client_errors_nudges import ClientErrorsNudges
from journal.features.client_errors.client_errors_options import ClientErrorsOptions
from journal.features.client_errors.support.client_errors_data_reader import REMINDER_TOOL_USES
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.viewer_console_error import ERROR, STACK, ViewerConsoleError
from tests.stories.fixtures.main.working_agent import WorkingAgent

ONE_ERROR = ClientErrorsNudges.errors(1)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(ClientErrorsOptions.REPORT, False)
def test_with_the_setting_off_the_agent_hears_nothing_of_the_viewers_errors(story):
    story.viewer_logs_a_console_error("y is null", "at Bar.vue:3")
    story.agent_reads()
    story.expect_agent_not_told(ClientErrorsNudges.LOGGED)
    story.expect_agent_not_told(ClientErrorsNudges.UNHANDLED)
    story.expect_stack(Ready)


@story(ViewerConsoleError, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_same_viewer_error_again_is_counted_and_not_told(story):
    story.viewer_logs_a_console_error(ERROR, STACK)
    story.expect_agent_not_told(ClientErrorsNudges.LOGGED)
    story.agent_runs("developer client-errors")
    story.expect_command_line(f"2x {ERROR}")
    story.expect_command_text(STACK)
    story.expect_stack(Ready)


@story(ViewerConsoleError, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_unhandled_viewer_error_is_named_again_at_the_reminder_tool_use_and_not_before(story):
    story.agent_reads(count=REMINDER_TOOL_USES - 1)
    story.expect_agent_not_told(ClientErrorsNudges.UNHANDLED)
    story.agent_reads()
    story.expect_agent_told(ClientErrorsNudges.UNHANDLED, errors=ONE_ERROR)
    story.expect_stack(Ready)


@story(ViewerConsoleError, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_clearing_the_viewer_errors_ends_the_reminders(story):
    story.agent_runs("developer client-errors --clear")
    story.expect_command_text("cleared")
    story.agent_reads(count=REMINDER_TOOL_USES + 1)
    story.expect_agent_not_told(ClientErrorsNudges.UNHANDLED)
    story.expect_stack(Ready)
