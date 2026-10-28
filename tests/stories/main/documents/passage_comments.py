from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

NOTES = "# Launch notes\n\n## Why\nBecause it is time.\n\n## How\nFirst the tag.\nThen the push.\nThen the notes."


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_comment_on_a_documents_passage_names_the_section_and_lines_it_sits_on(story):
    document = story.user_writes_a_document("Launch notes", "What it says, in one line", NOTES)
    comment = story.user_comments_on("docs", document, "> Then the push.\n> Then the notes.\n\nThe push comes before the tag here.")
    story.agent_runs(f"message read {comment}")
    story.expect_command_text(f"comments_on docs:{document}")
    story.expect_command_text(f"the passage sits in doc {document} at section 2, How, lines 8-9: `journal doc show {document} --section 2` or `--grep`")
    story.expect_stack(Ready)
