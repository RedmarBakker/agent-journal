from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reader_made_the_default_for_its_commands_names_the_one_it_takes_over_from(story):
    story.agent_runs(story.agents.subject, "reader add naps --commands sleep --pattern slept --about 'the naps'")
    story.agent_runs(story.agents.subject, "reader add rests --commands sleep --pattern rested --about 'the rests'")
    story.agent_runs(story.agents.subject, "reader default rests")
    story.expect_command_text("over naps")
    story.agent_runs(story.agents.subject, "reader list")
    story.expect_command_line("rests: the rests", "(the default for its commands)")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reader_written_anew_with_one_flag_keeps_what_it_picks(story):
    story.agent_runs(story.agents.subject, "reader add unit-runs --pattern '[0-9]+ passed' --about 'a unit runs summary' --label 'Running tests'")
    story.agent_runs(story.agents.subject, "reader add unit-runs --pattern '[0-9]+ (passed|failed)'")
    story.expect_command_passed()
    story.agent_runs(story.agents.subject, "reader list")
    story.expect_command_text("unit-runs: a unit runs summary")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_reader_without_what_it_picks_is_refused(story):
    story.agent_runs(story.agents.subject, "reader add fresh-one --pattern x")
    story.expect_command_text("a new reader states what it selects with --about")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_environment_overview_names_the_readers_kept_for_reading_outputs(story):
    story.agent_runs(story.agents.subject, "reader add failed-lines --pattern FAILED --about 'the failed tests of a pytest run'")
    story.agent_looks_at_the_overview(story.agents.subject)
    story.expect_command_text("== journal reader list ==")
    story.expect_command_text("failed-lines: the failed tests of a pytest run")
    story.expect_stack(story.agents.subject, Ready)
