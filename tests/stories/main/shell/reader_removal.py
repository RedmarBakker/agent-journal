from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.summary_reader import TEST_RUN, TEST_RUN_LINES, TEST_RUN_STATUS, SummaryReader


@story(SummaryReader, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_removing_a_reader_names_the_outputs_it_read_and_the_next_shell_line_is_answered(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, TEST_RUN, *TEST_RUN_LINES)
    story.agent_runs(story.agents.subject, f"output watch {output} --reader {story.readers.first}")
    result = story.agent_runs(story.agents.subject, f"reader remove {story.readers.first}")
    result.expect_command_text(f"outputs {output} were read through it")
    story.background_run_ends(story.agents.subject, output, TEST_RUN_STATUS)
    result = story.agent_runs(story.agents.subject, "output list")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready)
