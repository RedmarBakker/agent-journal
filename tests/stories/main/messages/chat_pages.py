from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PAGE = 25
SENT = 60


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_change_since_long_ago_is_a_page_at_most_and_only_rows_the_viewer_holds_and_newer(story):
    sent = [story.user_sends_message(f"m{n}") for n in range(SENT)]
    result = story.user_opens(f"/journal/messages?limit={PAGE}&since=1")
    result.expect_viewer_count_at_most("rows", PAGE + 1)
    result.expect_viewer_shows("is_last_page", False)
    held = sent[SENT - 10]
    result = story.user_opens(f"/journal/messages?limit={PAGE}&since=1&after={held}")
    result.expect_viewer_rows_newer("rows", held)
    story.expect_stack(story.agents.subject, Ready)
