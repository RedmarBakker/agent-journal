from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.errors_reader import ErrorsReader
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(ErrorsReader, subject=AgentRole.MAIN)
def test_an_output_searched_by_hand_for_a_readers_pattern_is_pointed_at_the_reader_once(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal output read {story.outputs.first} --grep error")
    result.expect_allowed()
    result.expect_agent_told(story.agents.subject, ShellNudges.READER_HINT, reader=story.readers.first)
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal output read {story.outputs.first} --grep error")
    result.expect_agent_not_told(story.agents.subject, ShellNudges.READER_HINT, reader=story.readers.first)
    story.expect_stack(story.agents.subject, Ready)


@story(ErrorsReader, subject=AgentRole.MAIN)
def test_a_reader_shows_the_lines_its_pattern_picks(story):
    result = story.agent_runs(story.agents.subject, f"output read {story.outputs.first} --reader {story.readers.first}")
    result.expect_command_passed()
    result.expect_command_text("an error")
    story.expect_stack(story.agents.subject, Ready)


@story(ErrorsReader, subject=AgentRole.MAIN)
def test_a_removed_reader_is_named_no_more(story):
    result = story.agent_runs(story.agents.subject, f"reader remove {story.readers.first}")
    result.expect_command_passed()
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal output read {story.outputs.first} --grep error")
    result.expect_agent_not_told(story.agents.subject, ShellNudges.READER_HINT, reader=story.readers.first)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_read_through_a_reader_that_does_not_exist_is_refused(story):
    output = story.agent_runs_a_command(story.agents.subject, "printf 'an error\\nfine\\n' | head -2")
    result = story.agent_runs(story.agents.subject, f"output read {output} --reader nobody")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)
