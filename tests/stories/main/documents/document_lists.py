from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

WRITTEN = 25
SHOWN = 20


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_documents_are_listed_a_page_at_a_time_without_their_body_and_read_whole_by_number(story):
    written = [story.user_writes_a_document(f"doc {n}", f"what doc {n} says", "the body") for n in range(WRITTEN)]
    result = story.user_opens("/journal/docs?limit=50")
    result.expect_viewer_rows("rows", "id", written[WRITTEN - SHOWN:])
    result.expect_viewer_shows("is_last_page", False)
    result.expect_viewer_rows_without("rows", "body")
    result = story.user_opens(f"/journal/docs?limit=50&before={written[WRITTEN - SHOWN]}")
    result.expect_viewer_rows("rows", "id", written[:WRITTEN - SHOWN])
    result = story.user_opens(f"/journal/docs/{written[-1]}")
    result.expect_viewer_shows("body", "the body")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_report_is_listed_without_its_body_and_its_items(story):
    story.user_writes_a_report("the report", "what was found", "what was found")
    result = story.user_opens("/journal/reports?limit=50")
    result.expect_viewer_rows_without("rows", "body")
    result.expect_viewer_rows_without("rows", "items")
    story.expect_stack(story.agents.subject, Ready)
