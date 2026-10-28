from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reader_made_the_default_for_its_commands_names_the_one_it_takes_over_from(story):
    story.agent_runs("reader add naps --commands sleep --pattern slept --about 'the naps'")
    story.agent_runs("reader add rests --commands sleep --pattern rested --about 'the rests'")
    story.agent_runs("reader default rests")
    story.expect_command_text("over naps")
    story.agent_runs("reader list")
    story.expect_command_line("rests: the rests", "(the default for its commands)")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reader_written_anew_with_one_flag_keeps_what_it_picks(story):
    story.agent_runs("reader add unit-runs --pattern '[0-9]+ passed' --about 'a unit runs summary' --label 'Running tests'")
    story.agent_runs("reader add unit-runs --pattern '[0-9]+ (passed|failed)'")
    story.expect_command_passed()
    story.agent_runs("reader list")
    story.expect_command_text("unit-runs: a unit runs summary")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_new_reader_without_what_it_picks_is_refused(story):
    story.agent_runs("reader add fresh-one --pattern x")
    story.expect_command_text("a new reader says what it picks with --about")
    story.expect_stack(Ready)
