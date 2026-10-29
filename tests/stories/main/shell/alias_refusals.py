from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.git_status_alias import GitStatusAlias
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_line_an_alias_runs_typed_by_hand_is_refused_with_the_alias(story):
    story.agent_runs_in_the_shell(story.agents.subject, "git status")
    story.expect_refused(story.agents.subject, ShellNudges.ALIASED_LINE, name=story.fixture.alias)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_alias_itself_goes_through_and_may_chain(story):
    story.agent_runs_in_the_shell(story.agents.subject, f"journal {story.fixture.alias} && ls")
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_line_that_starts_like_the_alias_but_runs_another_command_goes_through(story):
    story.agent_runs_in_the_shell(story.agents.subject, "git log")
    story.expect_allowed()
    story.expect_agent_not_told(story.agents.subject, ShellNudges.ALIASED_LINE, name=story.fixture.alias)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_alias_run_whose_line_a_longer_alias_runs_is_refused_with_the_longer(story):
    story.agent_runs(story.agents.subject, "alias add gts 'git status -s'")
    story.agent_runs_in_the_shell(story.agents.subject, f"journal {story.fixture.alias} -s")
    story.expect_refused(story.agents.subject, ShellNudges.MORE_SPECIFIC_ALIAS, name="gts", called=story.fixture.alias)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_edited_alias_refuses_its_new_line_and_lets_the_old_one_through(story):
    story.agent_runs(story.agents.subject, f"alias edit {story.fixture.alias} --line 'git diff'")
    story.expect_command_passed()
    story.agent_runs_in_the_shell(story.agents.subject, "git status")
    story.expect_allowed()
    story.agent_runs_in_the_shell(story.agents.subject, "git diff")
    story.expect_refused(story.agents.subject, ShellNudges.ALIASED_LINE, name=story.fixture.alias)
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_removed_alias_refuses_nothing(story):
    story.agent_runs(story.agents.subject, f"alias remove {story.fixture.alias}")
    story.expect_command_passed()
    story.agent_runs_in_the_shell(story.agents.subject, "git status")
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_alias_named_like_a_journal_command_is_refused(story):
    story.agent_runs(story.agents.subject, "alias add task 'git status'")
    story.expect_command_text("task is a journal command")
    story.expect_stack(story.agents.subject, Ready)


@story(GitStatusAlias, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_alias_named_like_another_alias_is_refused(story):
    story.agent_runs(story.agents.subject, f"alias add {story.fixture.alias} 'echo again'")
    story.expect_command_text(f"an alias named {story.fixture.alias} exists")
    story.expect_stack(story.agents.subject, Ready)
