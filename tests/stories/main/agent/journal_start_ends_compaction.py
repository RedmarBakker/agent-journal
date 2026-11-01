from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.compacting_task import CompactingTask


@story(CompactingTask, subject=AgentRole.MAIN)
def test_a_journal_start_ends_a_compaction_left_open_and_the_work_beneath_stays(story):
    story.journal_starts_again()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
