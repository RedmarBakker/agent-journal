from journal.features.pins.pins_nudges import PinsNudges
from journal.features.pins.pins_options import PinsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PULL_REQUEST = "https://github.com/acme/shop/pull/27"
SUGGESTION_INTERVAL = 3


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_link_an_edited_file_holds_is_never_suggested_as_a_pin(story):
    story.agent_has_edited_a_file_holding("a.py", "see https://example.com/docs/one")
    story.expect_agent_not_told(PinsNudges.LINK_PIN_REQUEST)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(PinsOptions.PIN_SUGGESTION_INTERVAL, SUGGESTION_INTERVAL)
def test_a_link_in_a_commands_output_is_suggested_as_a_pin_and_again_only_after_the_set_tool_uses(story):
    story.agent_has_run_printing("gh pr create", PULL_REQUEST)
    story.expect_agent_told(PinsNudges.LINK_PIN_REQUEST, url=PULL_REQUEST)
    story.agent_has_run_printing("gh pr view", PULL_REQUEST)
    story.expect_agent_not_told(PinsNudges.LINK_PIN_REQUEST)
    story.agent_reads(count=SUGGESTION_INTERVAL)
    story.agent_has_run_printing("gh pr view", PULL_REQUEST)
    story.expect_agent_told(PinsNudges.LINK_PIN_REQUEST, url=PULL_REQUEST)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_pinned_link_is_never_suggested(story):
    story.agent_runs(f"notice create 'Pull request 27' --link '{PULL_REQUEST}' --label 'Open it'")
    story.agent_reads(count=PinsOptions.PIN_SUGGESTION_INTERVAL.default)
    story.agent_has_run_printing("gh pr view", PULL_REQUEST)
    story.expect_agent_not_told(PinsNudges.LINK_PIN_REQUEST)
    story.expect_stack(Ready)
