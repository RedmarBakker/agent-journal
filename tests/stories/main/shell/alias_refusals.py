from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.git_status_alias import GitStatusAlias
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(GitStatusAlias, subject=AgentRole.MAIN)
def test_a_line_an_alias_runs_typed_by_hand_is_refused_with_the_alias(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "git status")
    result.expect_refused(story.agents.subject, ShellNudges.ALIASED_LINE, name=story.aliases.first)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, subject=AgentRole.MAIN)
def test_the_alias_itself_goes_through_and_may_chain(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal {story.aliases.first} && ls")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, subject=AgentRole.MAIN)
def test_a_line_that_starts_like_the_alias_but_runs_another_command_goes_through(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "git log")
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, ShellNudges.ALIASED_LINE, name=story.aliases.first)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, subject=AgentRole.MAIN)
def test_an_alias_run_whose_line_a_longer_alias_runs_is_refused_with_the_longer(story):
    story.agent_runs(story.agents.subject, "alias add gts 'git status -s'")
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal {story.aliases.first} -s")
    result.expect_refused(story.agents.subject, ShellNudges.MORE_SPECIFIC_ALIAS, name="gts", called=story.aliases.first)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, subject=AgentRole.MAIN)
def test_an_edited_alias_refuses_its_new_line_and_lets_the_old_one_through(story):
    result = story.agent_runs(story.agents.subject, f"alias edit {story.aliases.first} --line 'git diff'")
    result.expect_command_passed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "git status")
    result.expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "git diff")
    result.expect_refused(story.agents.subject, ShellNudges.ALIASED_LINE, name=story.aliases.first)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, subject=AgentRole.MAIN)
def test_a_removed_alias_refuses_nothing(story):
    result = story.agent_runs(story.agents.subject, f"alias remove {story.aliases.first}")
    result.expect_command_passed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "git status")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_alias_named_like_a_journal_command_is_refused(story):
    result = story.agent_runs(story.agents.subject, "alias add task 'git status'")
    result.expect_command_text("task is a journal command")
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, subject=AgentRole.MAIN)
def test_an_alias_named_like_another_alias_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"alias add {story.aliases.first} 'echo again'")
    result.expect_command_text(f"an alias named {story.aliases.first} exists")
    story.expect_stack(story.agents.subject, Ready)
