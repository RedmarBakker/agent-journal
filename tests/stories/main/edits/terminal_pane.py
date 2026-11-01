from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_shell_calls_parts_are_its_terminal_lines_once_the_call_has_finished(story):
    terminal = f"/journal/agents/{story.main_agent_id()}/terminal"
    story.agent_runs_in_the_shell(story.agents.subject, "ls src && git status")
    result = story.user_opens(terminal)
    result.expect_viewer_rows_count(0)
    story.agent_has_run_printing(story.agents.subject, "ls src && git status", "nothing to commit")
    result = story.user_opens(terminal)
    result.expect_viewer_list_field("command", ["ls src", "git status"])
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_journal_command_refused_for_its_chain_is_a_refused_line_in_the_terminal_and_its_retry_the_one_run(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task list && ls")
    result.expect_refused_by_anything()
    result = story.agent_runs_in_the_shell(story.agents.subject, "ls")
    result.expect_allowed()
    story.agent_has_run_printing(story.agents.subject, "ls", "a")
    result = story.user_opens(f"/journal/agents/{story.main_agent_id()}/terminal")
    result.expect_viewer_list_field("command", ["journal task list", "ls", "ls"])
    story.expect_stack(story.agents.subject, Ready)
