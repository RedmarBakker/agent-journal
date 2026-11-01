from journal.features.pins.pins_nudges import PinsNudges
from journal.features.pins.pins_options import PinsOptions
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PULL_REQUEST = "https://github.com/acme/shop/pull/27"
SUGGESTION_INTERVAL = 3


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(PinsOptions.PIN_SUGGESTION_INTERVAL, SUGGESTION_INTERVAL)
def test_a_link_in_a_commands_output_is_suggested_as_a_pin_and_again_only_after_the_set_tool_uses(story):
    result = story.agent_has_run_printing(story.agents.subject, "gh pr create", PULL_REQUEST)
    result.expect_agent_told(story.agents.subject, PinsNudges.LINK_PIN_REQUEST, url=PULL_REQUEST)
    result = story.agent_has_run_printing(story.agents.subject, "gh pr view", PULL_REQUEST)
    result.expect_agent_not_told(story.agents.subject, PinsNudges.LINK_PIN_REQUEST)
    story.agent_reads(story.agents.subject, count=SUGGESTION_INTERVAL)
    result = story.agent_has_run_printing(story.agents.subject, "gh pr view", PULL_REQUEST)
    result.expect_agent_told(story.agents.subject, PinsNudges.LINK_PIN_REQUEST, url=PULL_REQUEST)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_pinned_link_is_never_suggested(story):
    story.agent_runs(story.agents.subject, f"notice create 'Pull request 27' --link '{PULL_REQUEST}' --label 'Open it'")
    story.agent_reads(story.agents.subject, count=PinsOptions.PIN_SUGGESTION_INTERVAL.default)
    result = story.agent_has_run_printing(story.agents.subject, "gh pr view", PULL_REQUEST)
    result.expect_agent_not_told(story.agents.subject, PinsNudges.LINK_PIN_REQUEST)
    story.expect_stack(story.agents.subject, Ready)
