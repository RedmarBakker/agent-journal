from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
def test_an_output_searched_by_hand_for_a_readers_pattern_is_pointed_at_the_reader_once(story):
    story.agent_runs("reader add errors --pattern 'error' --about 'the error lines'")
    story.expect_command_passed()
    output = story.agent_runs_a_command("printf 'an error\\nfine\\n' | head -2")
    story.agent_runs_in_the_shell(f"journal output read {output} --grep error")
    story.expect_allowed()
    story.expect_agent_told(ShellNudges.READER_HINT, reader="errors")
    story.agent_runs_in_the_shell(f"journal output read {output} --grep error")
    story.expect_agent_not_told(ShellNudges.READER_HINT, reader="errors")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_removed_reader_is_named_no_more(story):
    story.agent_runs("reader add errors --pattern 'error' --about 'the error lines'")
    story.agent_runs("reader remove errors")
    story.expect_command_passed()
    output = story.agent_runs_a_command("printf 'an error\\nfine\\n' | head -2")
    story.agent_runs_in_the_shell(f"journal output read {output} --grep error")
    story.expect_agent_not_told(ShellNudges.READER_HINT, reader="errors")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_reader_shows_the_lines_its_pattern_picks(story):
    story.agent_runs("reader add errors --pattern 'error' --about 'the error lines'")
    output = story.agent_runs_a_command("printf 'an error\\nfine\\n' | head -2")
    story.agent_runs(f"output read {output} --reader errors")
    story.expect_command_passed()
    story.expect_command_text("an error")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_read_through_a_reader_that_does_not_exist_is_refused(story):
    output = story.agent_runs_a_command("printf 'an error\\nfine\\n' | head -2")
    story.agent_runs(f"output read {output} --reader nobody")
    story.expect_command_refused()
    story.expect_stack(Ready)
