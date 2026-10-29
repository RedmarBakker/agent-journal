from journal.features.tasks.feature import Tasks
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_feature_switched_off_takes_its_hold_with_it_so_a_stop_with_a_task_in_hand_goes_through(story):
    story.user_switches_off(Tasks)
    story.agent_stops(story.agents.subject)
    story.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
