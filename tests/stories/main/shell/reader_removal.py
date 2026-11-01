from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.summary_reader import TEST_RUN_LINES, TEST_RUN_STATUS, SummaryReader


@story(SummaryReader, subject=AgentRole.MAIN)
def test_removing_a_reader_names_the_outputs_it_read_and_the_next_shell_line_is_answered(story):
    story.agent_runs(story.agents.subject, f"output watch {story.outputs.first} --reader {story.readers.first}")
    result = story.agent_runs(story.agents.subject, f"reader remove {story.readers.first}")
    result.expect_command_text(f"outputs {story.outputs.first} were read through it")
    story.background_run_ends(story.agents.subject, story.outputs.first, *TEST_RUN_LINES, status=TEST_RUN_STATUS)
    result = story.agent_runs(story.agents.subject, "output list")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready)
