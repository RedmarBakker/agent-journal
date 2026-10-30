from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.fixtures.main.summary_reader import TEST_RUN, SummaryReader


@story(SummaryReader, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_removing_a_reader_names_the_outputs_it_read_and_the_next_shell_line_is_answered(story):
    output = story.agent_runs_a_command(story.agents.subject, TEST_RUN.format(seconds=story.setting(FOREGROUND_OPTION) * 2))
    story.agent_runs(story.agents.subject, f"output watch {output} --reader {story.readers.first}")
    result = story.agent_runs(story.agents.subject, f"reader remove {story.readers.first}")
    result.expect_command_text(f"outputs {output} were read through it")
    story.background_run_ends(output)
    result = story.agent_runs(story.agents.subject, "output list")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready)
