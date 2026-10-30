from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.fixtures.main.summary_reader import TEST_RUN, SummaryReader


@story(SummaryReader, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_line_that_an_awaited_output_ended_carries_what_its_reader_picks(story):
    output = story.agent_runs_a_command(story.agents.subject, TEST_RUN.format(seconds=story.setting(FOREGROUND_OPTION) * 2))
    story.agent_runs(story.agents.subject, f"await 'the tests' --output {output} --reader {story.readers.first}")
    story.background_run_ends(output)
    story.expect_typed(TasksNudges.WAIT_END.create(outcome=f"output {output} failed with code 1: 1 failed, 3 passed"))
    story.expect_stack(story.agents.subject, Ready)
