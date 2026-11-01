from journal.features.tasks.states.ready import Ready
from journal.http.controllers.agents import EDITS_SHOWN
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

OLDER_EDITS = 20


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_edits_pane_shows_an_edit_and_a_file_a_shell_line_wrote_with_their_lines_counted(story):
    story.agent_has_edited(story.agents.subject, "a.py")
    story.project_file("b.py", 2)
    story.agent_has_run_in_the_shell(story.agents.subject, "sed -i '' s/x/y/ b.py")
    result = story.user_opens(f"/journal/agents/{story.main_agent_id()}/edits")
    result.expect_viewer_rows("edits", "path", ["a.py", "b.py"])
    result.expect_viewer_rows("edits", "added", [1, 2])
    result.expect_viewer_rows("edits", "removed", [1, 0])
    result.expect_viewer_rows("edits", "first_line", [7, 1])
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_edits_pane_pages_back_through_the_kept_edits_and_says_when_none_is_older(story):
    story.repeat(EDITS_SHOWN + OLDER_EDITS, lambda: story.agent_has_edited(story.agents.subject, "a.py"))
    edits = f"/journal/agents/{story.main_agent_id()}/edits"
    result = story.user_opens(edits)
    result.expect_viewer_count("edits", EDITS_SHOWN)
    result.expect_viewer_shows("older", True)
    result = story.user_opens(f"{edits}?before={story.first_shown('edits')}")
    result.expect_viewer_count("edits", OLDER_EDITS)
    result.expect_viewer_shows("older", False)
    story.expect_stack(story.agents.subject, Ready)
