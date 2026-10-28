from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

WRITTEN = 25
SHOWN = 20


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_documents_are_listed_a_page_at_a_time_without_their_body_and_read_whole_by_number(story):
    written = [story.user_writes_a_document(f"doc {n}", f"what doc {n} says", "the body") for n in range(WRITTEN)]
    story.user_opens("/journal/docs?limit=50")
    story.expect_viewer_rows("rows", "id", written[WRITTEN - SHOWN:])
    story.expect_viewer_shows("is_last_page", False)
    story.expect_viewer_rows_without("rows", "body")
    story.user_opens(f"/journal/docs?limit=50&before={written[WRITTEN - SHOWN]}")
    story.expect_viewer_rows("rows", "id", written[:WRITTEN - SHOWN])
    story.user_opens(f"/journal/docs/{written[-1]}")
    story.expect_viewer_shows("body", "the body")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_report_is_listed_without_its_body_and_its_items(story):
    story.user_writes_a_report("the report", "what was found", "what was found")
    story.user_opens("/journal/reports?limit=50")
    story.expect_viewer_rows_without("rows", "body")
    story.expect_viewer_rows_without("rows", "items")
    story.expect_stack(Ready)
