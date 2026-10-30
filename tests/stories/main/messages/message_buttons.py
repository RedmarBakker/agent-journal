from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent

SETUP_PAGE = "http://localhost:8765/"
APP_FORM = "https://github.com/organizations/acme/settings/apps/new"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_message_carries_a_button_that_opens_an_address(story):
    result = story.agent_runs(story.agents.subject, f"message send 'The setup page is ready.' --button 'Open the setup page|{SETUP_PAGE}|opens the page in a new tab'")
    result.expect_command_passed()
    story.expect_message_buttons(story.newest("messages"), [{"label": "Open the setup page", "action": SETUP_PAGE, "note": "opens the page in a new tab", "method": "GET", "fields": {}}])
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_message_carries_a_button_that_posts_a_form_with_its_hidden_fields(story):
    result = story.agent_runs(story.agents.subject, f"message send 'Create the app for acme.' --form-button 'Create the app|{APP_FORM}|sends the app manifest to GitHub|manifest={{\"name\": \"acme deploys\"}}|state=one'")
    result.expect_command_passed()
    story.expect_message_buttons(story.newest("messages"), [{"label": "Create the app", "action": APP_FORM, "note": "sends the app manifest to GitHub", "method": "POST", "fields": {"manifest": '{"name": "acme deploys"}', "state": "one"}}])
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_button_to_an_address_that_is_not_a_web_address_is_refused_and_nothing_is_sent(story):
    before = story.newest("messages")
    result = story.agent_runs(story.agents.subject, "message send 'Click it.' --button 'Run it|javascript:alert(1)|runs it'")
    result.expect_command_refused()
    result.expect_command_text("http")
    story.expect_newest_message(before)
    story.expect_stack(story.agents.subject, Ready)


@story(ReadMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reply_carries_its_buttons(story):
    result = story.agent_runs(story.agents.subject, f"message send 'Here it is.' --reply-to {story.messages.first} --button 'Open the setup page|{SETUP_PAGE}|opens the page in a new tab'")
    result.expect_command_passed()
    story.expect_message(story.newest("messages"), reply_target=story.messages.first)
    story.expect_message_buttons(story.newest("messages"), [{"label": "Open the setup page", "action": SETUP_PAGE, "note": "opens the page in a new tab", "method": "GET", "fields": {}}])
    story.expect_stack(story.agents.subject, Ready)
