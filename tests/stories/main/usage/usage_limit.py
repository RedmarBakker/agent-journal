from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.usage.states.usage_limited import UsageLimited
from journal.features.usage.usage_nudges import UsageNudges
from journal.features.usage.usage_options import UsageOptions
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_turn_refused_on_the_usage_limit_holds_the_agent_once_and_types_nothing_while_it_holds(story):
    story.agent_turn_fails_on_the_usage_limit(story.agents.subject)
    story.agent_turn_fails_on_the_usage_limit(story.agents.subject)
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_typed()
    story.expect_stack(story.agents.subject, Ready, UsageLimited)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_users_message_ends_the_usage_hold_and_is_typed_at_once(story):
    story.agent_turn_fails_on_the_usage_limit(story.agents.subject)
    message = story.user_sends_message("are you there?")
    story.expect_typed(MessagesNudges.NEW_MESSAGE.create(n=message))
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_turn_is_tried_again_every_so_many_minutes_while_the_usage_limit_holds(story):
    story.agent_turn_fails_on_the_usage_limit(story.agents.subject)
    story.agent_is_quiet_for(story.agents.subject, story.setting(UsageOptions.CHECK_MINUTES) + 1)
    story.expect_typed(UsageNudges.LIMIT_CHECK.create())
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_turn_that_works_again_ends_the_usage_hold(story):
    story.agent_turn_fails_on_the_usage_limit(story.agents.subject)
    story.agent_reads(story.agents.subject)
    story.expect_stack(story.agents.subject, Ready)
