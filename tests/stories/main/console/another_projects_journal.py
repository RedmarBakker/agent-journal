from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

OTHER_PROJECT = "another-project"


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_command_from_another_project_that_finds_this_journal_on_its_port_is_refused_and_changes_nothing(story):
    result = story.another_projects_shell_runs(OTHER_PROJECT, "task create 'a task of the other project'")
    result.expect_refused_as_another_projects()
    result = story.user_opens("/journal/tasks")
    result.expect_viewer_rows_not_holding("rows", "title", "a task of the other project")
    result = story.another_projects_shell_runs(OTHER_PROJECT, "environment json")
    result.expect_refused_as_another_projects()
    result.expect_command_text_without("main")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_hook_from_another_projects_agent_is_refused_and_takes_no_place_among_this_journals_agents(story):
    result = story.another_projects_agent_hooks(OTHER_PROJECT, "SessionStart")
    result.expect_refused_as_another_projects()
    result = story.user_opens("/journal/agents")
    result.expect_viewer_rows_not_holding("rows", "session", "another-project-session")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_command_naming_this_project_goes_through(story):
    result = story.this_projects_shell_runs("task create 'a task of this project'")
    result.expect_command_passed()
    result = story.user_opens("/journal/tasks")
    result.expect_viewer_rows_holding("rows", "title", "a task of this project")
    story.expect_stack(story.agents.subject, Ready)
