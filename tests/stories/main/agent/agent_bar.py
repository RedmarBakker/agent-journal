from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_agent_bars_pickers_name_the_providers_choices_and_type_its_command(story):
    result = story.user_opens("/journal/agents/controls/claude?model=opus&effort=high")
    result.expect_viewer_rows("groups", "key", ["model", "effort", "context"])
    result.expect_viewer_part(("groups", 0, "current"), "opus")
    result = story.user_presses(f"/journal/agents/{story.main_agent_id()}/control", {"action": "effort", "value": "max"})
    result.expect_viewer_shows("queued", True)
    story.expect_typed_last("/effort max")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_model_the_provider_does_not_offer_is_refused_by_the_agent_bar(story):
    result = story.user_presses(f"/journal/agents/{story.main_agent_id()}/control", {"action": "model", "value": "gpt"})
    result.expect_viewer_refused("")
    story.expect_stack(story.agents.subject, Ready)
