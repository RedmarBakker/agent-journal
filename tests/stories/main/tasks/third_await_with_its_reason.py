from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.task_queue import TaskQueue

AWAIT = "journal await 'the build' --until false"
REASON = "the build decides which file I touch next"


@story(TaskQueue, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_await_of_unknown_length_with_open_work_is_refused_twice_and_accepted_the_third_time_with_its_reason_said_back(story):
    story.agent_runs_in_the_shell(story.agents.subject, AWAIT)
    story.expect_refused(story.agents.subject, TasksNudges.WAIT_SWITCH_REFUSAL)
    story.agent_runs_in_the_shell(story.agents.subject, AWAIT)
    story.expect_refused(story.agents.subject, TasksNudges.WAIT_SWITCH_REFUSAL)
    story.agent_runs_in_the_shell(story.agents.subject, AWAIT)
    story.expect_refused(story.agents.subject, TasksNudges.WAIT_REASON_REQUEST)
    story.agent_runs_in_the_shell(story.agents.subject, f'{AWAIT} --why "{REASON}"')
    story.expect_agent_told(story.agents.subject, TasksNudges.WAIT_REASON_LINE, why=REASON)
    story.expect_stack(story.agents.subject, Ready, Working)
