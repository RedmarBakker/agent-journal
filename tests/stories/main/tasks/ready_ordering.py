from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(TasksOptions.AUTO, True)
def test_aged_work_with_unknown_delivery_history_is_not_starved_by_new_priority_work(story):
    changed = story.user_presses("/journal/settings", {"estimates": {"mode": "report"}})
    changed.expect_viewer_passed()
    aged = story.agent_creates_task(story.agents.subject, "the older unestimated task")
    story.time_travel(days=1)
    recent = story.agent_runs(story.agents.subject, "task create 'the urgent task' --priority critical")
    recent.expect_command_passed()
    urgent = story.task_number()

    result = story.agent_runs(story.agents.subject, f"task complete {story.tasks.started} --how done")

    result.expect_command_passed()
    story.expect_task(aged, state=TaskState.STARTED)
    story.expect_task(urgent, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, Working)
