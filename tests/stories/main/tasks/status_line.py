from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, subject=AgentRole.MAIN)
def test_the_status_line_names_the_task_in_hand_and_what_the_agent_is_stuck_on(story):
    result = story.user_opens("/journal/summary")
    result.expect_viewer_part(("environments", 0, "task", "id"), story.tasks.started)
    result.expect_viewer_part(("environments", 0, "task", "wait_text"), "")
    story.agent_runs(story.agents.subject, "stuck 'stuck on the login'")
    result = story.user_opens("/journal/summary")
    result.expect_viewer_part(("environments", 0, "task", "wait_text"), "stuck on the login")
    story.expect_stack(story.agents.subject, Ready, Working, Impasse)
