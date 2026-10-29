from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_agents_page_shows_the_stack_top_first_with_what_the_top_waits_for(story):
    story.agent_runs(story.agents.subject, "stuck lost")
    story.user_opens(f"/journal/agents?ids={story.main_agent_id()}")
    story.expect_viewer_part(("rows", 0, "stack", 0, "name"), Impasse.name)
    story.expect_viewer_part(("rows", 0, "stack", 1, "name"), Working.name)
    story.expect_viewer_part(("rows", 0, "stack", 2, "name"), Ready.name)
    story.expect_task(story.tasks.started, state="started")
    story.expect_stack(story.agents.subject, Ready, Working, Impasse)
