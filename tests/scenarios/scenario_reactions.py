from journal.features.messages.messages_nudges import MessagesNudges
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
def test_the_users_reaction_to_a_reply_is_told_to_the_agent(scenario):
    message = scenario.user_sends_message("is the footer done?")
    reply = scenario.agent_replies_with_number(message, "it is")
    scenario.user_reacts(reply, "🎉")
    scenario.expect_agent_told(MessagesNudges.USER_REACTION, n=reply)
