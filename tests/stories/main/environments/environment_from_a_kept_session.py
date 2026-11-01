from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

SESSION = "old-session"


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_new_environment_is_filled_from_a_kept_claude_session_once_and_the_form_names_where_it_went(story):
    story.a_claude_session_is_kept(SESSION, "Fix the login page", "Fixed the login page.")
    result = story.user_opens("/journal/environments/sessions")
    result.expect_viewer_list_field("first_prompt", ["Fix the login page"])
    story.user_posted("/journal/environments", {"name": "login", "provider": "claude", "session": SESSION})
    result = story.user_opens_in("login", "/journal/messages")
    result.expect_viewer_rows_holding("rows", "text", "Fix the login page")
    result.expect_viewer_rows_holding("rows", "text", "Fixed the login page.")
    result = story.user_presses("/journal/environments", {"name": "login", "provider": "claude", "session": SESSION})
    result.expect_viewer_refused("")
    result = story.user_opens("/journal/environments/sessions")
    result.expect_viewer_list_field("environment", ["login"])
    story.expect_stack(story.agents.subject, Ready)
