from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.repositories.repository import PAGE_ROWS
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.message_with_file import MessageWithFile


@story(MessageWithFile, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_file_attached_to_a_message_long_ago_is_still_listed_on_the_attachments_page(story):
    story.repeat(PAGE_ROWS, lambda: story.user_sends_message("another message"))
    result = story.user_opens("/journal/attachments")
    result.expect_viewer_rows_holding("files", "name", "shot one.png")
    result.expect_viewer_shows("total", 1)
    story.expect_stack(story.agents.subject, Ready)
