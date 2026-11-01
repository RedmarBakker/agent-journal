from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.summary_reader import TEST_RUN_LINES, TEST_RUN_STATUS, SummaryReader


@story(SummaryReader, subject=AgentRole.MAIN)
def test_the_line_that_an_awaited_output_ended_carries_what_its_reader_picks(story):
    story.agent_runs(story.agents.subject, f"await 'the tests' --output {story.outputs.first} --reader {story.readers.first}")
    story.background_run_ends(story.agents.subject, story.outputs.first, *TEST_RUN_LINES, status=TEST_RUN_STATUS)
    story.expect_typed(TasksNudges.WAIT_END.create(outcome=f"output {story.outputs.first} failed with code 1: 1 failed, 3 passed"))
    story.expect_stack(story.agents.subject, Ready)
