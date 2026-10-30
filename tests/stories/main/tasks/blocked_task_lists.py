from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_blocked_task_is_listed_with_its_open_wait(story):
    opening = story.user_posted("/journal/tasks", {"title": "the prerequisite"})["id"]
    blocked = story.user_posted("/journal/tasks", {"title": "the dependent"})["id"]
    story.user_posted(f"/journal/tasks/{blocked}/block", {"on": [f"task:{opening}"]})
    story.user_opens("/journal/tasks?limit=10")
    story.expect_viewer_passed()
    story.expect_viewer_rows("rows", "waits", [[], [f"tasks:{opening}"]])
    story.expect_stack(story.agents.subject, Ready)
